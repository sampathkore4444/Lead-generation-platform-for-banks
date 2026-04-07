"""
Authentication Middleware
JWT token verification and user authentication
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional

from ..config.settings import settings
from ..config.database import SessionLocal, get_db
from ..models.user import User, UserRole
from ..schemas.user import TokenPayload


# Security scheme
security = HTTPBearer(auto_error=False)


def decode_token(token: str) -> Optional[TokenPayload]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return TokenPayload(**payload)
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Requires valid Bearer token.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = db.query(User).filter(User.username == payload.sub).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled"
        )

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db=Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Used for endpoints that support both authenticated and anonymous access.
    """
    if not credentials:
        return None

    return await get_current_user(credentials, db)


def require_role(*roles: UserRole):
    """
    Dependency factory for requiring specific user roles.
    Usage: require_role(UserRole.BRANCH_MANAGER, UserRole.IT_ADMIN)
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}",
            )
        return current_user

    return role_checker


# Pre-built role dependencies
require_sales_rep = require_role(UserRole.SALES_REP)
require_branch_manager = require_role(UserRole.BRANCH_MANAGER)
require_compliance_officer = require_role(UserRole.COMPLIANCE_OFFICER)
require_it_admin = require_role(UserRole.IT_ADMIN)
