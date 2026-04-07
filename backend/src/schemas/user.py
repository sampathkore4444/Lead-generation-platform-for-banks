"""
User Schemas
Pydantic schemas for user request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""

    SALES_REP = "sales_rep"
    BRANCH_MANAGER = "branch_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    IT_ADMIN = "it_admin"


# ============ Request Schemas ============


class UserCreate(BaseModel):
    """Schema for creating a new user"""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    password: str = Field(
        ..., min_length=8, max_length=100, description="User password"
    )
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    role: UserRole = Field(default=UserRole.SALES_REP, description="User role")
    branch_id: Optional[int] = Field(None, description="Branch ID")


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(
        None, min_length=2, max_length=100, description="Full name"
    )
    role: Optional[UserRole] = Field(None, description="User role")
    branch_id: Optional[int] = Field(None, description="Branch ID")
    is_active: Optional[bool] = Field(None, description="Whether user is active")


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password"""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=100, description="New password"
    )


class UserLogin(BaseModel):
    """Schema for user login"""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class UserMFAEnable(BaseModel):
    """Schema for enabling MFA"""

    code: str = Field(
        ..., min_length=6, max_length=6, description="MFA verification code"
    )


# ============ Response Schemas ============


class UserResponse(BaseModel):
    """Schema for user response"""

    id: int
    email: str
    username: str
    full_name: str
    role: UserRole
    branch_id: Optional[int]
    is_active: bool
    mfa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for user list response"""

    id: int
    email: str
    username: str
    full_name: str
    role: UserRole
    branch_id: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True


# ============ Token Schemas ============


class Token(BaseModel):
    """Schema for authentication token"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """Schema for token payload"""

    sub: str  # username
    exp: int
    iat: int
    type: str = "access"


# ============ Branch Schemas ============


class BranchResponse(BaseModel):
    """Schema for branch response"""

    id: int
    name: str
    code: str
    address: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BranchListResponse(BaseModel):
    """Schema for branch list response"""

    id: int
    name: str
    code: str
    is_active: bool

    class Config:
        from_attributes = True
