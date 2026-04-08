"""
Lead Service
Handles lead business logic and operations
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..models.lead import Lead, LeadAuditLog, DuplicateLog, LeadStatus
from ..models.user import User
from ..schemas.lead import LeadCreate, LeadUpdate, LeadStatusUpdate, LeadStatsResponse


class LeadService:
    """Service for handling lead operations"""

    # Duplicate check window (days)
    DUPLICATE_WINDOW_DAYS = 30

    @staticmethod
    def check_duplicate(db: Session, phone: str) -> Optional[Lead]:
        """Check if phone number has duplicate submission within window"""
        window_start = datetime.utcnow() - timedelta(
            days=LeadService.DUPLICATE_WINDOW_DAYS
        )

        duplicate = (
            db.query(Lead)
            .filter(and_(Lead.phone == phone, Lead.created_at >= window_start))
            .first()
        )

        return duplicate

    @staticmethod
    def create_lead(
        db: Session,
        lead_data: LeadCreate,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Lead:
        """Create a new lead with duplicate checking"""
        # Check for duplicate
        existing_lead = LeadService.check_duplicate(db, lead_data.phone)

        if existing_lead:
            # Increment resubmit count
            existing_lead.resubmit_count += 1
            db.commit()

            # Log duplicate attempt
            log = DuplicateLog(phone=lead_data.phone, lead_id=existing_lead.id)
            db.add(log)
            db.commit()

            # Raise exception (will be handled by route)
            raise ValueError(
                f"Duplicate lead exists from {existing_lead.created_at.strftime('%Y-%m-%d')}"
            )

        # Create new lead
        lead = Lead(
            full_name=lead_data.full_name,
            phone=lead_data.phone,
            lao_id=lead_data.lao_id,
            product=lead_data.product,
            amount=lead_data.amount,
            preferred_time=lead_data.preferred_time,
            consent_given=lead_data.consent_given,
            status=LeadStatus.NEW,
        )

        db.add(lead)
        db.flush()

        # Create audit log
        audit = LeadAuditLog(
            lead_id=lead.id,
            action="create",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(audit)
        db.commit()

        return lead

    @staticmethod
    def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
        """Get lead by ID"""
        return db.query(Lead).filter(Lead.id == lead_id).first()

    @staticmethod
    def get_leads_for_user(
        db: Session,
        user_id: int,
        status: Optional[LeadStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Lead]:
        """Get leads assigned to a user"""
        query = db.query(Lead).filter(Lead.assigned_to == user_id)

        if status:
            query = query.filter(Lead.status == status)

        return query.order_by(Lead.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_leads_for_branch(
        db: Session,
        branch_id: int,
        status: Optional[LeadStatus] = None,
        user_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Lead]:
        """Get leads for a branch (manager view)

        Includes:
        - Leads assigned to this branch
        - Unassigned leads (branch_id is NULL) - so managers can assign them
        """
        # Include leads for this branch OR unassigned leads
        query = db.query(Lead).filter(
            or_(Lead.branch_id == branch_id, Lead.branch_id.is_(None))
        )

        if status:
            query = query.filter(Lead.status == status)

        if user_id:
            query = query.filter(Lead.assigned_to == user_id)

        return query.order_by(Lead.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def update_lead_status(
        db: Session,
        lead_id: int,
        status_update: LeadStatusUpdate,
        user: User,
        ip_address: Optional[str] = None,
    ) -> Optional[Lead]:
        """Update lead status"""
        lead = LeadService.get_lead(db, lead_id)

        if not lead:
            return None

        old_status = lead.status
        lead.status = status_update.status

        # Update notes if provided
        if status_update.notes:
            lead.notes = (
                lead.notes or ""
            ) + f"\n[{datetime.utcnow().isoformat()}] {status_update.notes}"

        # Set first contact time
        if status_update.status == LeadStatus.CONTACTED and not lead.first_contact_at:
            lead.first_contact_at = datetime.utcnow()

        # Set converted time
        if status_update.status == LeadStatus.CONVERTED and not lead.converted_at:
            lead.converted_at = datetime.utcnow()

        db.commit()

        # Create audit log
        audit = LeadAuditLog(
            lead_id=lead.id,
            user_id=user.id,
            action="status_change",
            old_status=old_status.value,
            new_status=status_update.status.value,
            details=status_update.notes,
            ip_address=ip_address,
        )
        db.add(audit)
        db.commit()

        return lead

    @staticmethod
    def assign_lead(
        db: Session,
        lead_id: int,
        user_id: int,
        assigned_by: User,
        ip_address: Optional[str] = None,
    ) -> Optional[Lead]:
        """Assign lead to a user"""
        lead = LeadService.get_lead(db, lead_id)

        if not lead:
            return None

        old_assigned = lead.assigned_to
        lead.assigned_to = user_id

        db.commit()

        # Create audit log
        audit = LeadAuditLog(
            lead_id=lead.id,
            user_id=assigned_by.id,
            action="assign",
            old_status=str(old_assigned) if old_assigned else None,
            new_status=str(user_id),
            ip_address=ip_address,
        )
        db.add(audit)
        db.commit()

        return lead

    @staticmethod
    def get_lead_stats(
        db: Session, branch_id: Optional[int] = None, user_id: Optional[int] = None
    ) -> LeadStatsResponse:
        """Get lead statistics
        
        For branch managers: includes unassigned leads (branch_id is NULL)
        For sales reps: only shows leads assigned to them
        """
        # Base query
        query = db.query(Lead)

        if branch_id:
            # Include leads for this branch OR unassigned leads
            query = query.filter(
                or_(Lead.branch_id == branch_id, Lead.branch_id.is_(None))
            )

        if user_id:
            query = query.filter(Lead.assigned_to == user_id)

        # Get counts
        total = query.count()
        new_count = query.filter(Lead.status == LeadStatus.NEW).count()
        contacted_count = query.filter(Lead.status == LeadStatus.CONTACTED).count()
        qualified_count = query.filter(Lead.status == LeadStatus.QUALIFIED).count()
        converted_count = query.filter(Lead.status == LeadStatus.CONVERTED).count()
        lost_count = query.filter(Lead.status == LeadStatus.LOST).count()

        # Calculate conversion rate
        closed = converted_count + lost_count
        conversion_rate = (converted_count / closed * 100) if closed > 0 else 0.0

        # Calculate average time to contact (in minutes)
        contacted_leads = query.filter(
            and_(Lead.first_contact_at.isnot(None), Lead.created_at.isnot(None))
        ).all()

        if contacted_leads:
            total_time = sum(
                [
                    (lead.first_contact_at - lead.created_at).total_seconds() / 60
                    for lead in contacted_leads
                ]
            )
            avg_time_to_contact = total_time / len(contacted_leads)
        else:
            avg_time_to_contact = 0.0

        # Calculate SLA compliance (% contacted within 60 minutes)
        sla_threshold = datetime.utcnow() - timedelta(minutes=60)
        sla_compliant = query.filter(
            and_(
                Lead.status.in_(
                    [LeadStatus.CONTACTED, LeadStatus.QUALIFIED, LeadStatus.CONVERTED]
                ),
                Lead.first_contact_at <= sla_threshold,
            )
        ).count()

        contacted_or_qualified = contacted_count + qualified_count + converted_count
        sla_compliance = (
            (sla_compliant / contacted_or_qualified * 100)
            if contacted_or_qualified > 0
            else 100.0
        )

        return LeadStatsResponse(
            total=total,
            new_count=new_count,
            contacted_count=contacted_count,
            qualified_count=qualified_count,
            converted_count=converted_count,
            lost_count=lost_count,
            conversion_rate=conversion_rate,
            avg_time_to_contact=avg_time_to_contact,
            sla_compliance=sla_compliance,
        )

    @staticmethod
    def log_lead_view(
        db: Session, lead_id: int, user: User, ip_address: Optional[str] = None
    ) -> None:
        """Log lead view action"""
        audit = LeadAuditLog(
            lead_id=lead_id, user_id=user.id, action="view", ip_address=ip_address
        )
        db.add(audit)
        db.commit()

    @staticmethod
    def log_lead_export(
        db: Session, lead_ids: List[int], user: User, ip_address: Optional[str] = None
    ) -> None:
        """Log lead export action"""
        audit = LeadAuditLog(
            lead_id=None,
            user_id=user.id,
            action="export",
            details=f"Exported {len(lead_ids)} leads: {', '.join(map(str, lead_ids))}",
            ip_address=ip_address,
        )
        db.add(audit)
        db.commit()
