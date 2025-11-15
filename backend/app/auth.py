from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db_sync
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Allow requests without Authorization header in MVP mode
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db_sync)
) -> User:
    """Get current authenticated user from JWT token.

    In MVP mode (no auth), this function will return a default persisted user
    so downstream endpoints continue to work without requiring tokens.
    If an Authorization header is provided and valid, the real user is returned.
    """

    # If credentials provided, try to verify token as before
    if credentials and getattr(credentials, "credentials", None):
        token = credentials.credentials
        payload = verify_token(token)

        if payload is not None:
            # Get email from payload
            email = payload.get("email")
            if email:
                user = db.query(User).filter(User.email == email).first()
                if user and getattr(user, "is_active", True):
                    return user

    # Fallback for MVP: return or create a default dev user
    mvp_email = settings.MVP_USER_EMAIL
    user = db.query(User).filter(User.email == mvp_email).first()
    if user:
        return user

    # Create a lightweight MVP user
    user = User(email=mvp_email, full_name="MVP User", is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
