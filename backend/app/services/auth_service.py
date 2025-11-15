from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, MagicToken
from app.auth import create_access_token, create_refresh_token
from app.utils import generate_random_token
from app.services.email import send_magic_link_email


class AuthService:
    
    @staticmethod
    async def send_magic_link(email: str, db: AsyncSession) -> dict:
        """Generate and send magic link to user's email"""
        
        # Generate token
        token = generate_random_token(32)
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # Save token to database
        magic_token = MagicToken(
            email=email,
            token=token,
            expires_at=expires_at,
            used=False
        )
        db.add(magic_token)
        await db.commit()
        
        # Send email
        await send_magic_link_email(email, token)
        
        return {"message": "Magic link sent", "email": email}
    
    @staticmethod
    async def verify_magic_token(token: str, db: AsyncSession) -> Optional[dict]:
        """Verify magic token and create/login user"""
        
        # Find token in database
        result = await db.execute(
            select(MagicToken).where(
                MagicToken.token == token,
                MagicToken.used == False,
                MagicToken.expires_at > datetime.utcnow()
            )
        )
        magic_token = result.scalar_one_or_none()
        
        if not magic_token:
            return None
        
        # Mark token as used
        magic_token.used = True
        
        # Get or create user
        result = await db.execute(
            select(User).where(User.email == magic_token.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                email=magic_token.email,
                is_active=True
            )
            db.add(user)
        
        await db.commit()
        await db.refresh(user)
        
        # Generate JWT tokens
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }
    
    @staticmethod
    async def get_current_user(user_id: int, db: AsyncSession) -> Optional[User]:
        """Get current user by ID"""
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user(user_id: int, full_name: str, db: AsyncSession) -> Optional[User]:
        """Update user information"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.full_name = full_name
            await db.commit()
            await db.refresh(user)
        
        return user
