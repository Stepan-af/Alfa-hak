from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import (
    MagicLinkRequest,
    MagicLinkResponse,
    TokenRequest,
    TokenResponse,
    UserResponse,
    UserUpdate
)
from app.services.auth_service import AuthService
from app.auth import verify_token

router = APIRouter()


@router.post("/login_magic", response_model=MagicLinkResponse)
async def send_magic_link(
    request: MagicLinkRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send magic link to user's email"""
    result = await AuthService.send_magic_link(request.email, db)
    return MagicLinkResponse(**result)


@router.post("/token", response_model=TokenResponse)
async def verify_magic_token(
    request: TokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify magic token and return JWT tokens"""
    result = await AuthService.verify_magic_token(request.token, db)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return TokenResponse(**result)


async def get_current_user_dependency(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Dependency to get current user from JWT token"""
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = await AuthService.get_current_user(int(user_id), db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.get("/users/me", response_model=UserResponse)
async def get_current_user(
    current_user = Depends(get_current_user_dependency)
):
    """Get current user profile"""
    return current_user


@router.post("/users/update", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    user = await AuthService.update_user(
        current_user.id,
        update_data.full_name,
        db
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/logout")
async def logout():
    """Logout user (client should remove tokens)"""
    return {"message": "Successfully logged out"}
