"""
Lead Model
Database model for leads (customer inquiries)
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    Index,
    Numeric,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..config.database import Base


class LeadStatus(str, enum.Enum):
    """Lead status enumeration - Banking Sales Lifecycle"""

    NEW = "new"  # Lead created from form submission
    INITIAL_CONTACT = "initial_contact"  # First contact attempted
    NEEDS_ASSESSMENT = "needs_assessment"  # Gathering requirements
    QUALIFICATION = "qualification"  # Checking eligibility
    PROPOSAL = "proposal"  # Presenting options
    NEGOTIATION = "negotiation"  # Discussing terms
    CONVERTED = "converted"  # Customer converted (opened account)
    LOST = "lost"  # Lead lost/not interested


class ProductType(str, enum.Enum):
    """Product type enumeration"""

    SAVINGS_ACCOUNT = "savings_account"
    PERSONAL_LOAN = "personal_loan"
    HOME_LOAN = "home_loan"
    CREDIT_CARD = "credit_card"


class PreferredTime(str, enum.Enum):
    """Preferred contact time enumeration"""

    MORNING = "morning"  # 8:00 - 12:00
    AFTERNOON = "afternoon"  # 13:00 - 17:00
    EVENING = "evening"  # 17:00 - 20:00


class Lead(Base):
    """Lead model representing customer inquiries"""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    lao_id = Column(String(15), nullable=False)
    product = Column(Enum(ProductType), nullable=False)
    amount = Column(Numeric(15, 0), nullable=True)
    preferred_time = Column(Enum(PreferredTime), nullable=True)
    consent_given = Column(Boolean, default=False, nullable=False)
    status = Column(
        Enum(LeadStatus), default=LeadStatus.NEW, nullable=False, index=True
    )
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    resubmit_count = Column(Integer, default=0)
    is_duplicated = Column(Boolean, default=False)
    first_contact_at = Column(DateTime, nullable=True)
    converted_at = Column(DateTime, nullable=True)
    anonymized_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Automation fields
    stage = Column(String(50), default="new", nullable=False, index=True)
    stage_changed_at = Column(DateTime, nullable=True)
    last_contacted_at = Column(DateTime, nullable=True)
    last_contact_method = Column(
        String(20), nullable=True
    )  # call, whatsapp, line, email
    documents_verified = Column(Boolean, default=False)
    documents_verified_at = Column(DateTime, nullable=True)
    auto_progressed = Column(Boolean, default=False)

    # Relationships
    branch = relationship("Branch", back_populates="leads")
    assigned_to_user = relationship("User", back_populates="leads")
    audit_logs = relationship("LeadAuditLog", back_populates="lead")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_leads_phone_created", "phone", "created_at"),
        Index("idx_leads_status_created", "status", "created_at"),
        Index("idx_leads_assigned_created", "assigned_to", "created_at"),
    )


class LeadAuditLog(Base):
    """Lead audit log model for tracking all lead-related actions"""

    __tablename__ = "lead_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(
        String(50), nullable=False
    )  # view, create, update_status, export, delete
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    lead = relationship("Lead", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_audit_lead_created", "lead_id", "created_at"),
        Index("idx_audit_user_created", "user_id", "created_at"),
    )


class DuplicateLog(Base):
    """Duplicate submission log model"""

    __tablename__ = "duplicate_logs"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Index
    __table_args__ = (Index("idx_duplicate_phone", "phone", "attempted_at"),)
