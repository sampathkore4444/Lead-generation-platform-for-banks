"""
Lead Schemas
Pydantic schemas for lead request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import enum


class ProductType(str, enum.Enum):
    """Product type enumeration"""

    SAVINGS_ACCOUNT = "savings_account"
    PERSONAL_LOAN = "personal_loan"
    HOME_LOAN = "home_loan"
    CREDIT_CARD = "credit_card"


class PreferredTime(str, enum.Enum):
    """Preferred contact time enumeration"""

    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class LeadStatus(str, enum.Enum):
    """Lead status enumeration"""

    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


# ============ Request Schemas ============


class LeadCreate(BaseModel):
    """Schema for creating a new lead from customer"""

    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    phone: str = Field(
        ..., min_length=9, max_length=20, description="Lao phone number (20XXXXXXXX)"
    )
    lao_id: str = Field(..., min_length=13, max_length=15, description="Lao ID number")
    product: ProductType = Field(..., description="Product interest")
    amount: Optional[int] = Field(
        None, ge=1000000, le=500000000, description="Loan amount in LAK"
    )
    preferred_time: Optional[PreferredTime] = Field(
        None, description="Preferred contact time"
    )
    consent_given: bool = Field(..., description="Customer consent")

    @validator("phone")
    def validate_phone(cls, v):
        """Validate Lao phone number format"""
        # Remove any spaces or dashes
        phone = v.replace(" ", "").replace("-", "")
        # Must start with 20 and be 9 digits after
        if not phone.startswith("20") or len(phone) != 11:
            raise ValueError("Phone must be in format 20XXXXXXXX (9 digits after 20)")
        return phone

    @validator("lao_id")
    def validate_lao_id(cls, v):
        """Validate Lao ID format"""
        lao_id = v.replace(" ", "").replace("-", "")
        if not lao_id.isdigit():
            raise ValueError("Lao ID must contain only digits")
        return lao_id

    @validator("product")
    def validate_product(cls, v, values):
        """Validate loan amount for loan products"""
        product = v
        amount = values.get("amount")
        if product in [ProductType.PERSONAL_LOAN, ProductType.HOME_LOAN] and not amount:
            raise ValueError(f"Loan amount required for {product.value}")
        return v


class LeadUpdate(BaseModel):
    """Schema for updating a lead"""

    notes: Optional[str] = Field(None, description="Notes about the lead")
    assigned_to: Optional[int] = Field(None, description="User ID to assign lead to")
    preferred_time: Optional[PreferredTime] = Field(
        None, description="Preferred contact time"
    )


class LeadStatusUpdate(BaseModel):
    """Schema for updating lead status"""

    status: LeadStatus = Field(..., description="New lead status")
    notes: Optional[str] = Field(None, description="Notes about status change")
    lost_reason: Optional[str] = Field(None, description="Reason if status is 'lost'")

    @validator("lost_reason")
    def validate_lost_reason(cls, v, values):
        """Validate lost reason if status is lost"""
        if values.get("status") == LeadStatus.LOST and not v:
            raise ValueError("Lost reason required when marking lead as lost")
        return v


class LeadAssign(BaseModel):
    """Schema for assigning lead to a user"""

    assigned_to: int = Field(..., description="User ID to assign lead to")


# ============ Response Schemas ============


class LeadResponse(BaseModel):
    """Schema for lead response"""

    id: int
    full_name: str
    phone: str
    lao_id: str
    product: ProductType
    amount: Optional[int]
    preferred_time: Optional[PreferredTime]
    consent_given: bool
    status: LeadStatus
    branch_id: Optional[int]
    assigned_to: Optional[int]
    notes: Optional[str]
    resubmit_count: int
    first_contact_at: Optional[datetime]
    converted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Schema for lead list response (PII hidden)"""

    id: int
    full_name: str
    phone: str
    phone_masked: str
    product: ProductType
    amount: Optional[int]
    preferred_time: Optional[PreferredTime]
    status: LeadStatus
    assigned_to: Optional[int]
    assigned_to_name: Optional[str]
    created_at: datetime
    age_minutes: int

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_age(cls, obj):
        """Create response with calculated age"""
        data = obj.__dict__.copy()
        # Calculate age in minutes
        if obj.created_at:
            age = datetime.utcnow() - obj.created_at
            data["age_minutes"] = int(age.total_seconds() / 60)
        else:
            data["age_minutes"] = 0
        # Mask phone number
        if obj.phone and len(obj.phone) >= 4:
            data["phone_masked"] = f"****{obj.phone[-4:]}"
        else:
            data["phone_masked"] = "****"
        # Get assigned user name
        if obj.assigned_to_user:
            data["assigned_to_name"] = obj.assigned_to_user.full_name
        else:
            data["assigned_to_name"] = None
        return cls(**{k: v for k, v in data.items() if k in cls.model_fields})


class LeadStatsResponse(BaseModel):
    """Schema for lead statistics"""

    total: int
    new_count: int
    contacted_count: int
    qualified_count: int
    converted_count: int
    lost_count: int
    conversion_rate: float
    avg_time_to_contact: float
    sla_compliance: float


class DuplicateCheckResponse(BaseModel):
    """Schema for duplicate check response"""

    is_duplicate: bool
    original_lead_id: Optional[int]
    original_submission_date: Optional[datetime]
    message: str


# ============ Audit Schemas ============


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""

    id: int
    lead_id: int
    user_id: Optional[int]
    user_name: Optional[str]
    action: str
    old_status: Optional[str]
    new_status: Optional[str]
    details: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Export Schemas ============


class LeadExport(BaseModel):
    """Schema for lead CSV export"""

    id: int
    full_name: str
    phone: str
    lao_id: str
    product: str
    amount: Optional[int]
    preferred_time: Optional[str]
    status: str
    assigned_to: Optional[str]
    notes: Optional[str]
    created_at: datetime
    converted_at: Optional[datetime]
