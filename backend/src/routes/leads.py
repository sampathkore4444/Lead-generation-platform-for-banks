"""
Lead Routes
Handles lead CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import csv
import io
from datetime import datetime, timedelta

from ..config.database import get_db
from ..schemas.lead import (
    LeadCreate,
    LeadResponse,
    LeadListResponse,
    LeadStatsResponse,
    LeadStatusUpdate,
    LeadAssign,
    DuplicateCheckResponse,
)
from ..services.lead_service import LeadService
from ..middleware.auth import (
    get_current_user,
    require_sales_rep,
    require_branch_manager,
)
from ..models.user import User, UserRole


router = APIRouter()


# ============ Public Routes ============


@router.post("", status_code=status.HTTP_201_CREATED, response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate, request: Request, db: Session = Depends(get_db)
):
    """
    Create a new lead from customer form.
    Public endpoint - no authentication required.
    """
    try:
        lead = LeadService.create_lead(
            db=db,
            lead_data=lead_data,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return lead
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/duplicate-check", response_model=DuplicateCheckResponse)
async def check_duplicate(
    phone: str = Query(..., description="Phone number to check"),
    db: Session = Depends(get_db),
):
    """
    Check if phone number has duplicate submission.
    Public endpoint for form validation.
    """
    duplicate = LeadService.check_duplicate(db, phone)

    if duplicate:
        return DuplicateCheckResponse(
            is_duplicate=True,
            original_lead_id=duplicate.id,
            original_submission_date=duplicate.created_at,
            message=f"You already submitted a request on {duplicate.created_at.strftime('%Y-%m-%d')}. A representative will contact you soon.",
        )

    return DuplicateCheckResponse(
        is_duplicate=False,
        original_lead_id=None,
        original_submission_date=None,
        message="No duplicate found",
    )


# ============ Protected Routes (Requires Authentication) ============


@router.get("", response_model=List[LeadListResponse])
async def get_leads(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get leads for current user.
    Sales reps see their assigned leads.
    Managers see all branch leads.
    """
    # Convert status string to enum
    status_enum = None
    if status:
        from ..models.lead import LeadStatus

        try:
            status_enum = LeadStatus(status)
        except ValueError:
            pass

    # Get leads based on role
    if current_user.role == UserRole.SALES_REP:
        leads = LeadService.get_leads_for_user(
            db=db,
            user_id=current_user.id,
            status=status_enum,
            limit=limit,
            offset=offset,
        )
    elif current_user.role in [
        UserRole.BRANCH_MANAGER,
        UserRole.COMPLIANCE_OFFICER,
        UserRole.IT_ADMIN,
    ]:
        leads = LeadService.get_leads_for_branch(
            db=db,
            branch_id=current_user.branch_id,
            status=status_enum,
            limit=limit,
            offset=offset,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Convert to response format
    return [
        LeadListResponse(
            id=lead.id,
            full_name=lead.full_name,
            phone=lead.phone,
            phone_masked=f"****{lead.phone[-4:]}" if lead.phone else "****",
            product=lead.product,
            amount=lead.amount,
            preferred_time=lead.preferred_time,
            status=lead.status,
            assigned_to=lead.assigned_to,
            assigned_to_name=(
                lead.assigned_to_user.full_name if lead.assigned_to_user else None
            ),
            created_at=lead.created_at,
            age_minutes=(
                int((datetime.utcnow() - lead.created_at).total_seconds() / 60)
                if lead.created_at
                else 0
            ),
        )
        for lead in leads
    ]


@router.get("/stats", response_model=LeadStatsResponse)
async def get_lead_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get lead statistics for current user/branch.
    """
    if current_user.role == UserRole.SALES_REP:
        return LeadService.get_lead_stats(db, user_id=current_user.id)
    else:
        return LeadService.get_lead_stats(db, branch_id=current_user.branch_id)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get lead details by ID.
    Requires authentication.
    """
    lead = LeadService.get_lead(db, lead_id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    # Log the view
    LeadService.log_lead_view(
        db=db,
        lead_id=lead_id,
        user=current_user,
        ip_address=request.client.host if request.client else None,
    )

    return lead


@router.patch("/{lead_id}/status", response_model=LeadResponse)
async def update_lead_status(
    lead_id: int,
    status_update: LeadStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update lead status.
    Requires authentication.
    """
    lead = LeadService.update_lead_status(
        db=db,
        lead_id=lead_id,
        status_update=status_update,
        user=current_user,
        ip_address=request.client.host if request.client else None,
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    return lead


@router.patch("/{lead_id}/assign", response_model=LeadResponse)
async def assign_lead(
    lead_id: int,
    assign_data: LeadAssign,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Assign lead to a different user.
    Requires branch manager or IT admin.
    """
    if current_user.role not in [UserRole.BRANCH_MANAGER, UserRole.IT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can assign leads",
        )

    lead = LeadService.assign_lead(
        db=db,
        lead_id=lead_id,
        user_id=assign_data.assigned_to,
        assigned_by=current_user,
        ip_address=request.client.host if request.client else None,
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    return lead


@router.get("/export/csv")
async def export_leads_csv(
    request: Request,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export leads to CSV format.
    Requires authentication.
    """
    # Get leads
    status_enum = None
    if status:
        from ..models.lead import LeadStatus

        try:
            status_enum = LeadStatus(status)
        except ValueError:
            pass

    if current_user.role == UserRole.SALES_REP:
        leads = LeadService.get_leads_for_user(
            db=db, user_id=current_user.id, status=status_enum, limit=1000
        )
    else:
        leads = LeadService.get_leads_for_branch(
            db=db, branch_id=current_user.branch_id, status=status_enum, limit=1000
        )

    # Log the export
    LeadService.log_lead_export(
        db=db,
        lead_ids=[lead.id for lead in leads],
        user=current_user,
        ip_address=request.client.host if request.client else None,
    )

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "ID",
            "Full Name",
            "Phone",
            "Lao ID",
            "Product",
            "Amount",
            "Preferred Time",
            "Status",
            "Assigned To",
            "Notes",
            "Created At",
            "Converted At",
        ]
    )

    # Data
    for lead in leads:
        writer.writerow(
            [
                lead.id,
                lead.full_name,
                lead.phone,
                lead.lao_id,
                lead.product.value,
                lead.amount,
                lead.preferred_time.value if lead.preferred_time else "",
                lead.status.value,
                lead.assigned_to_user.full_name if lead.assigned_to_user else "",
                lead.notes or "",
                lead.created_at.isoformat() if lead.created_at else "",
                lead.converted_at.isoformat() if lead.converted_at else "",
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"},
    )


# ============ AI Suggestions ============


class NextBestActionResponse(BaseModel):
    """Schema for next best action response"""

    lead_id: int
    suggested_stage: str
    action: str
    reason: str
    urgency: str  # high, medium, low
    tips: List[str]


@router.get("/suggestions/{lead_id}", response_model=NextBestActionResponse)
async def get_lead_suggestion(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get AI-powered next best action for a lead.
    Based on lead data and current stage, suggest the next best action.
    """
    lead = LeadService.get_lead(db, lead_id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    # Determine suggestion based on current status
    stage_suggestions = {
        "new": {
            "suggested_stage": "initial_contact",
            "action": "Make first contact call",
            "reason": "Lead is new and needs immediate first contact",
            "urgency": "high",
            "tips": [
                "Call within 30 minutes for best conversion",
                "Introduce yourself and STBank products",
                "Ask about their needs and preferences",
            ],
        },
        "initial_contact": {
            "suggested_stage": "needs_assessment",
            "action": "Gather requirements",
            "reason": "First contact made, assess customer needs",
            "urgency": "high",
            "tips": [
                "Document customer requirements",
                "Identify product fit",
                "Schedule follow-up call",
            ],
        },
        "needs_assessment": {
            "suggested_stage": "qualification",
            "action": "Check eligibility",
            "reason": "Requirements gathered, verify eligibility",
            "urgency": "medium",
            "tips": [
                "Verify ID documents",
                "Check credit history",
                "Confirm income requirements",
            ],
        },
        "qualification": {
            "suggested_stage": "proposal",
            "action": "Prepare proposal",
            "reason": "Lead qualified, prepare product proposal",
            "urgency": "medium",
            "tips": [
                "Prepare personalized product offer",
                "Calculate optimal terms",
                "Prepare comparison with competitors",
            ],
        },
        "proposal": {
            "suggested_stage": "negotiation",
            "action": "Present and negotiate",
            "reason": "Proposal presented, discuss terms",
            "urgency": "medium",
            "tips": [
                "Present proposal to customer",
                "Address any objections",
                "Negotiate terms if needed",
            ],
        },
        "negotiation": {
            "suggested_stage": "converted",
            "action": "Close the deal",
            "reason": "Terms agreed, finalize the account opening",
            "urgency": "high",
            "tips": [
                "Schedule branch visit for account opening",
                "Prepare final documents",
                "Celebrate the conversion!",
            ],
        },
        "converted": {
            "suggested_stage": "converted",
            "action": "Maintain relationship",
            "reason": "Lead converted, focus on retention",
            "urgency": "low",
            "tips": [
                "Send welcome package",
                "Schedule 1-week follow-up",
                "Cross-sell other products",
            ],
        },
        "lost": {
            "suggested_stage": "lost",
            "action": "Review and learn",
            "reason": "Lead lost, analyze for improvements",
            "urgency": "low",
            "tips": [
                "Document loss reason",
                "Ask for feedback",
                "Add to nurture list for future",
            ],
        },
    }

    current_status = lead.status.value if lead.status else "new"
    suggestion = stage_suggestions.get(current_status, stage_suggestions["new"])

    # Check if lead is stale (not contacted in 24h)
    from datetime import datetime, timedelta

    stale_threshold = datetime.utcnow() - timedelta(hours=24)
    is_stale = lead.status in ["new", "initial_contact", "needs_assessment"] and (
        not lead.first_contact_at or lead.created_at < stale_threshold
    )

    if is_stale and suggestion["urgency"] != "high":
        suggestion["urgency"] = "high"
        suggestion["reason"] = f"⚠️ Lead is stale - not contacted in 24h!"
        suggestion["tips"].insert(0, "URGENT: Contact immediately!")

    return NextBestActionResponse(
        lead_id=lead_id,
        suggested_stage=suggestion["suggested_stage"],
        action=suggestion["action"],
        reason=suggestion["reason"],
        urgency=suggestion["urgency"],
        tips=suggestion["tips"],
    )


# ============ Automation Routes ============

from ..services.automation_service import AutomationService


@router.post("/automation/call/{lead_id}")
async def trigger_call_automation(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger automation when a call is made to a lead.
    Automatically moves lead from NEW to INITIAL_CONTACT stage.
    """
    lead = AutomationService.process_call_made(db, lead_id, current_user.id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    return {
        "success": True,
        "message": f"Call logged for lead {lead_id}",
        "lead_id": lead.id,
        "new_stage": lead.stage.value,
        "auto_progressed": True,
    }


@router.post("/automation/whatsapp/{lead_id}")
async def trigger_whatsapp_automation(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger automation when a WhatsApp message is sent to a lead.
    Automatically moves lead from NEW to INITIAL_CONTACT stage.
    """
    lead = AutomationService.process_whatsapp_sent(db, lead_id, current_user.id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    return {
        "success": True,
        "message": f"WhatsApp message logged for lead {lead_id}",
        "lead_id": lead.id,
        "new_stage": lead.stage.value,
        "auto_progressed": True,
    }


@router.post("/automation/line/{lead_id}")
async def trigger_line_automation(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger automation when a LINE message is sent to a lead.
    Automatically moves lead from NEW to INITIAL_CONTACT stage.
    """
    lead = AutomationService.process_line_sent(db, lead_id, current_user.id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    return {
        "success": True,
        "message": f"LINE message logged for lead {lead_id}",
        "lead_id": lead.id,
        "new_stage": lead.stage.value,
        "auto_progressed": True,
    }


@router.post("/automation/document-verified/{lead_id}")
async def trigger_document_automation(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger automation when documents are verified for a lead.
    Automatically moves lead to QUALIFICATION stage.
    """
    lead = AutomationService.process_document_verified(db, lead_id, current_user.id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    return {
        "success": True,
        "message": f"Document verification logged for lead {lead_id}",
        "lead_id": lead.id,
        "new_stage": lead.stage.value,
        "auto_progressed": True,
    }


@router.post("/automation/process-stale")
async def process_stale_leads(
    stale_hours: int = Query(
        24, description="Hours after which lead is considered stale"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_rep),
):
    """
    Process all stale leads and auto-progress them to next stage.
    Typically called by a scheduled job.
    """
    updated_leads = AutomationService.process_stale_leads(db, stale_hours)

    return {
        "success": True,
        "message": f"Processed {len(updated_leads)} stale leads",
        "processed_count": len(updated_leads),
        "stale_hours": stale_hours,
        "updated_leads": [
            {"id": lead.id, "name": lead.full_name, "old_stage": lead.stage.value}
            for lead in updated_leads
        ],
    }


@router.get("/automation/stale-report")
async def get_stale_leads_report(
    stale_hours: int = Query(
        24, description="Hours after which lead is considered stale"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a report of stale leads without auto-progressing them.
    """
    report = AutomationService.get_stale_leads_report(db, stale_hours)

    return report
