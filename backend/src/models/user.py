"""
User Model
Database model for users (employees)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..config.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""

    SALES_REP = "sales_rep"
    BRANCH_MANAGER = "branch_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    IT_ADMIN = "it_admin"


class User(Base):
    """User model representing bank employees"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=True)  # For local auth fallback
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.SALES_REP)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # MFA fields
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    mfa_backup_codes = Column(String(500), nullable=True)
    mfa_enabled_at = Column(DateTime, nullable=True)
    
    # LDAP fields
    ldap_username = Column(String(100), nullable=True)
    auth_method = Column(String(20), default="local")  # local, ldap, oauth
    
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    branch = relationship("Branch", back_populates="users")
    leads = relationship("Lead", back_populates="assigned_to_user")
    audit_logs = relationship("LeadAuditLog", back_populates="user")


class Branch(Base):
    """Branch model representing bank branches"""

    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    address = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="branch")
    leads = relationship("Lead", back_populates="branch")
