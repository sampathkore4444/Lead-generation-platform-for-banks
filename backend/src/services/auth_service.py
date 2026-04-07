"""
Authentication Service
Handles user authentication and token generation
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..models.user import User
from ..schemas.user import Token, TokenPayload


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling authentication operations"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(username: str) -> str:
        """Create JWT access token"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

        payload = {"sub": username, "exp": expire, "iat": now, "type": "access"}

        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def create_refresh_token(username: str) -> str:
        """Create JWT refresh token"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=settings.refresh_token_expire_minutes)

        payload = {"sub": username, "exp": expire, "iat": now, "type": "refresh"}

        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def create_tokens(username: str) -> Token:
        """Create both access and refresh tokens"""
        return Token(
            access_token=AuthService.create_access_token(username),
            refresh_token=AuthService.create_refresh_token(username),
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,  # Convert to seconds
        )

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        # Find user by username or email
        user = (
            db.query(User)
            .filter((User.username == username) | (User.email == username))
            .first()
        )

        if not user:
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def update_last_login(db: Session, user: User) -> None:
        """Update user's last login timestamp"""
        user.last_login = datetime.utcnow()
        db.commit()

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Token]:
        """Create new access token from refresh token"""
        try:
            payload = jwt.decode(
                refresh_token, settings.secret_key, algorithms=[settings.algorithm]
            )

            if payload.get("type") != "refresh":
                return None

            username = payload.get("sub")
            if not username:
                return None

            # Create new tokens
            return AuthService.create_tokens(username)

        except jwt.JWTError:
            return None
