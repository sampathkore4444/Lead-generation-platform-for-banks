"""
Automation Service
Handles automatic stage progression based on various triggers
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from ..models.lead import Lead
from ..models.user import User
from ..services.lead_service import LeadService

logger = logging.getLogger(__name__)


class LeadStage:
    """Lead stage constants for automation"""

    NEW = "new"
    INITIAL_CONTACT = "initial_contact"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "lost"


class AutomationService:
    """Service for automating lead stage progression"""

    # Stage progression rules (using string values)
    STAGE_PROGRESSION = {
        LeadStage.NEW: LeadStage.INITIAL_CONTACT,
        LeadStage.INITIAL_CONTACT: LeadStage.QUALIFICATION,
        LeadStage.QUALIFICATION: LeadStage.PROPOSAL,
        LeadStage.PROPOSAL: LeadStage.NEGOTIATION,
        LeadStage.NEGOTIATION: LeadStage.CLOSED_WON,
    }

    # Time-based auto-progression hours (configurable)
    DEFAULT_STALE_HOURS = 24

    @staticmethod
    def process_call_made(db: Session, lead_id: int, user_id: int) -> Optional[Lead]:
        """
        Process a call made to a lead.
        If lead is in NEW stage, move to INITIAL_CONTACT.

        Args:
            db: Database session
            lead_id: Lead ID
            user_id: User who made the call

        Returns:
            Updated lead or None
        """
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return None

        # Update last contact info
        lead.last_contacted_at = datetime.utcnow()
        lead.last_contact_method = "call"

        # Auto-progress from NEW to INITIAL_CONTACT
        if lead.stage == LeadStage.NEW:
            old_stage = lead.stage
            lead.stage = LeadStage.INITIAL_CONTACT
            lead.stage_changed_at = datetime.utcnow()

            # Create audit log
            LeadService.create_audit_log(
                db=db,
                lead_id=lead.id,
                user_id=user_id,
                action="stage_change",
                old_value=old_stage.value,
                new_value=LeadStage.INITIAL_CONTACT.value,
                details=f"Auto-progressed due to call made",
            )
            logger.info(
                f"Lead {lead_id} auto-progressed from {old_stage} to {LeadStage.INITIAL_CONTACT} due to call"
            )

        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def process_whatsapp_sent(
        db: Session, lead_id: int, user_id: int
    ) -> Optional[Lead]:
        """
        Process a WhatsApp message sent to a lead.
        If lead is in NEW stage, move to INITIAL_CONTACT.

        Args:
            db: Database session
            lead_id: Lead ID
            user_id: User who sent the message

        Returns:
            Updated lead or None
        """
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return None

        # Update last contact info
        lead.last_contacted_at = datetime.utcnow()
        lead.last_contact_method = "whatsapp"

        # Auto-progress from NEW to INITIAL_CONTACT
        if lead.stage == LeadStage.NEW:
            old_stage = lead.stage
            lead.stage = LeadStage.INITIAL_CONTACT
            lead.stage_changed_at = datetime.utcnow()

            LeadService.create_audit_log(
                db=db,
                lead_id=lead.id,
                user_id=user_id,
                action="stage_change",
                old_value=old_stage.value,
                new_value=LeadStage.INITIAL_CONTACT.value,
                details=f"Auto-progressed due to WhatsApp message sent",
            )
            logger.info(
                f"Lead {lead_id} auto-progressed from {old_stage} to {LeadStage.INITIAL_CONTACT} due to WhatsApp"
            )

        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def process_line_sent(db: Session, lead_id: int, user_id: int) -> Optional[Lead]:
        """
        Process a LINE message sent to a lead.
        If lead is in NEW stage, move to INITIAL_CONTACT.

        Args:
            db: Database session
            lead_id: Lead ID
            user_id: User who sent the message

        Returns:
            Updated lead or None
        """
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return None

        # Update last contact info
        lead.last_contacted_at = datetime.utcnow()
        lead.last_contact_method = "line"

        # Auto-progress from NEW to INITIAL_CONTACT
        if lead.stage == LeadStage.NEW:
            old_stage = lead.stage
            lead.stage = LeadStage.INITIAL_CONTACT
            lead.stage_changed_at = datetime.utcnow()

            LeadService.create_audit_log(
                db=db,
                lead_id=lead.id,
                user_id=user_id,
                action="stage_change",
                old_value=old_stage.value,
                new_value=LeadStage.INITIAL_CONTACT.value,
                details=f"Auto-progressed due to LINE message sent",
            )
            logger.info(
                f"Lead {lead_id} auto-progressed from {old_stage} to {LeadStage.INITIAL_CONTACT} due to LINE"
            )

        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def process_document_verified(
        db: Session, lead_id: int, user_id: int
    ) -> Optional[Lead]:
        """
        Process document verification for a lead.
        Move to QUALIFICATION stage if documents are verified.

        Args:
            db: Database session
            lead_id: Lead ID
            user_id: User who verified the documents

        Returns:
            Updated lead or None
        """
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return None

        # Update document status
        lead.documents_verified = True
        lead.documents_verified_at = datetime.utcnow()

        # Auto-progress to QUALIFICATION if in INITIAL_CONTACT or earlier
        if lead.stage in [LeadStage.NEW, LeadStage.INITIAL_CONTACT]:
            old_stage = lead.stage
            lead.stage = LeadStage.QUALIFICATION
            lead.stage_changed_at = datetime.utcnow()

            LeadService.create_audit_log(
                db=db,
                lead_id=lead.id,
                user_id=user_id,
                action="stage_change",
                old_value=old_stage.value,
                new_value=LeadStage.QUALIFICATION.value,
                details=f"Auto-progressed due to document verification",
            )
            logger.info(
                f"Lead {lead_id} auto-progressed from {old_stage} to {LeadStage.QUALIFICATION} due to document verification"
            )

        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def process_stale_leads(db: Session, stale_hours: int = None) -> List[Lead]:
        """
        Process leads that haven't been contacted in specified hours.
        Auto-progress stale leads to next stage.

        Args:
            db: Database session
            stale_hours: Hours after which a lead is considered stale (default: 24)

        Returns:
            List of updated leads
        """
        if stale_hours is None:
            stale_hours = AutomationService.DEFAULT_STALE_HOURS

        stale_threshold = datetime.utcnow() - timedelta(hours=stale_hours)

        # Import LeadStatus enum
        from ..models.lead import LeadStatus
        
        # Find leads that haven't been contacted in X hours
        # and are not in final stages
        stale_leads = (
            db.query(Lead)
            .filter(
                Lead.stage.in_(
                    [
                        LeadStage.NEW,
                        LeadStage.INITIAL_CONTACT,
                        LeadStage.QUALIFICATION,
                        LeadStage.PROPOSAL,
                        LeadStage.NEGOTIATION,
                    ]
                ),
                Lead.status == LeadStatus.NEW,
                (Lead.last_contacted_at == None)
                | (Lead.last_contacted_at < stale_threshold),
            )
            .all()
        )

        updated_leads = []
        system_user_id = 0  # System user ID for automated actions

        for lead in stale_leads:
            # Determine next stage
            next_stage = AutomationService.STAGE_PROGRESSION.get(lead.stage)

            if next_stage and lead.stage != LeadStage.CLOSED_WON:
                old_stage = lead.stage
                lead.stage = next_stage
                lead.stage_changed_at = datetime.utcnow()
                lead.auto_progressed = True

                LeadService.create_audit_log(
                    db=db,
                    lead_id=lead.id,
                    user_id=system_user_id,
                    action="stage_change",
                    old_value=old_stage.value,
                    new_value=next_stage.value,
                    details=f"Auto-progressed due to inactivity ({stale_hours}h without contact)",
                )

                updated_leads.append(lead)
                logger.info(
                    f"Lead {lead.id} auto-progressed from {old_stage} to {next_stage} due to stale ({stale_hours}h)"
                )

        db.commit()

        # Refresh all updated leads
        for lead in updated_leads:
            db.refresh(lead)

        return updated_leads

    @staticmethod
    def get_stale_leads_report(db: Session, stale_hours: int = None) -> Dict:
        """
        Get a report of stale leads without auto-progressing them.

        Args:
            db: Database session
            stale_hours: Hours after which a lead is considered stale

        Returns:
            Dictionary with stale leads count by stage
        """
        from ..models.lead import LeadStatus
        
        if stale_hours is None:
            stale_hours = AutomationService.DEFAULT_STALE_HOURS

        stale_threshold = datetime.utcnow() - timedelta(hours=stale_hours)

        # Count leads by stage that are stale
        stale_by_stage = {}

        for stage in [
            LeadStage.NEW,
            LeadStage.INITIAL_CONTACT,
            LeadStage.QUALIFICATION,
            LeadStage.PROPOSAL,
            LeadStage.NEGOTIATION,
        ]:
            count = (
                db.query(Lead)
                .filter(
                    Lead.stage == stage,
                    Lead.status == LeadStatus.NEW,
                    (Lead.last_contacted_at == None)
                    | (Lead.last_contacted_at < stale_threshold),
                )
                .count()
            )

            if count > 0:
                stale_by_stage[stage.value] = count

        return {
            "stale_hours": stale_hours,
            "total_stale": sum(stale_by_stage.values()),
            "by_stage": stale_by_stage,
        }
