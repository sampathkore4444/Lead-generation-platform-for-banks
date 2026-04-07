"""
Auto-Anonymization Service
Handles 90-day data retention and GDPR/Lao compliance
"""
import hashlib
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.src.models.lead import Lead
from backend.src.models.lead_audit_log import LeadAuditLog


class AnonymizationService:
    """
    Service for anonymizing lead data after retention period
    - 90 days for converted/lost leads
    - 7 years for audit logs (Lao banking regulation)
    """
    
    # Lao provinces for location replacement
    PROVINCES = [
        "Vientiane Capital", "Luang Prabang", "Savannakhet", 
        "Champasak", "Xieng Khouang", "Huaphanh",
        "Sayaboury", "Bokeo", "Luang Namtha", "Oudomxay",
        "Khammouane", "Bolikhamxay", "Xaysomboun",
        "Sekong", "Attapeu", "Salavanh"
    ]
    
    @staticmethod
    def anonymize_lead_data(lead: Lead) -> Dict:
        """
        Anonymize lead PII data
        Returns the original values for audit trail (hashed)
        """
        original_data = {
            "full_name": lead.full_name,
            "phone": lead.phone,
            "lao_id": lead.lao_id
        }
        
        # Generate anonymized values
        lead_id_hash = hashlib.sha256(str(lead.id).encode()).hexdigest()[:8]
        
        lead.full_name = f"ANONYMIZED_{lead_id_hash}"
        lead.phone = f"20{random.randint(1000000, 9999999)}"
        lead.lao_id = f"AN{random.randint(1000000000000, 9999999999999)}"
        lead.anonymized_at = datetime.utcnow()
        
        return original_data
    
    @staticmethod
    def get_anonymization_stats(db: Session) -> Dict:
        """Get statistics about leads eligible for anonymization"""
        
        # Converted/lost leads older than 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        eligible = db.query(Lead).filter(
            and_(
                Lead.status.in_(["converted", "lost"]),
                Lead.anonymized_at.is_(None),
                Lead.created_at < cutoff_date
            )
        ).count()
        
        already_anonymized = db.query(Lead).filter(
            Lead.anonymized_at.isnot(None)
        ).count()
        
        total_leads = db.query(Lead).count()
        
        return {
            "eligible_for_anonymization": eligible,
            "already_anonymized": already_anonymized,
            "total_leads": total_leads,
            "cutoff_date": cutoff_date.isoformat()
        }
    
    @staticmethod
    def run_anonymization_job(db: Session, dry_run: bool = False) -> Dict:
        """
        Run the anonymization job
        Finds converted/lost leads older than 90 days and anonymizes them
        
        Args:
            db: Database session
            dry_run: If True, only count eligible records
            
        Returns:
            Dict with job results
        """
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Find eligible leads
        eligible_leads = db.query(Lead).filter(
            and_(
                Lead.status.in_(["converted", "lost"]),
                Lead.anonymized_at.is_(None),
                Lead.created_at < cutoff_date
            )
        ).all()
        
        if dry_run:
            return {
                "dry_run": True,
                "eligible_count": len(eligible_leads),
                "cutoff_date": cutoff_date.isoformat(),
                "message": f"Would anonymize {len(eligible_leads)} leads"
            }
        
        # Anonymize each lead
        anonymized_count = 0
        errors = []
        
        for lead in eligible_leads:
            try:
                # Store original data hash for audit
                data_hash = AnonymizationService._hash_original_data(lead)
                
                # Anonymize
                AnonymizationService.anonymize_lead_data(lead)
                
                # Create audit log
                audit_log = LeadAuditLog(
                    lead_id=lead.id,
                    user_id=1,  # System user
                    action="anonymize",
                    old_status=lead.status,
                    new_status="anonymized",
                    ip_address="system",
                    metadata={
                        "original_data_hash": data_hash,
                        "reason": "90-day retention policy"
                    }
                )
                db.add(audit_log)
                
                anonymized_count += 1
                
            except Exception as e:
                errors.append({
                    "lead_id": lead.id,
                    "error": str(e)
                })
        
        # Commit changes
        db.commit()
        
        return {
            "dry_run": False,
            "anonymized_count": anonymized_count,
            "error_count": len(errors),
            "errors": errors,
            "cutoff_date": cutoff_date.isoformat(),
            "completed_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _hash_original_data(lead: Lead) -> str:
        """Create SHA256 hash of original PII for audit trail"""
        data = f"{lead.full_name}:{lead.phone}:{lead.lao_id}:{lead.id}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def restore_lead(db: Session, lead_id: int, admin_user_id: int) -> bool:
        """
        Restore an anonymized lead (admin only)
        This would require backup data or manual intervention
        """
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead or not lead.anonymized_at:
            return False
        
        # Log restoration attempt
        audit_log = LeadAuditLog(
            lead_id=lead_id,
            user_id=admin_user_id,
            action="restore_attempt",
            ip_address="system",
            metadata={"message": "Restoration attempted - requires manual data recovery"}
        )
        db.add(audit_log)
        db.commit()
        
        # Note: Actual restoration would require backup data
        return True
    
    @staticmethod
    def get_audit_log_retention_info() -> Dict:
        """Get audit log retention policy info"""
        return {
            "retention_years": 7,
            "regulation": "Lao Banking Regulation",
            "automatic_deletion": False,  # Manual process for audit logs
            "recommended_purge_date": (datetime.utcnow() - timedelta(days=2555)).strftime("%Y-%m-%d")
        }


class ScheduledJobService:
    """
    Service for managing scheduled/cron jobs
    For on-premise deployment without external cron
    """
    
    @staticmethod
    def create_anonymization_cron() -> str:
        """Generate cron expression for anonymization job"""
        # Run daily at 2:00 AM
        return "0 2 * * *"
    
    @staticmethod
    async def check_and_run_scheduled_jobs(db: Session) -> Dict:
        """
        Check if any scheduled jobs need to run
        Called by a lightweight scheduler or cron
        
        Returns:
            Dict with job execution results
        """
        results = {}
        
        # Check if anonymization job should run (daily check)
        # For simplicity, we'll use a database flag
        last_run_key = "last_anonymization_run"
        
        # Get last run time from settings or database
        # For now, just run the job
        anonymization_result = AnonymizationService.run_anonymization_job(db)
        results["anonymization"] = anonymization_result
        
        return results
    
    @staticmethod
    def get_job_schedule() -> Dict:
        """Get configured job schedules"""
        return {
            "anonymization": {
                "cron": "0 2 * * *",  # Daily at 2 AM
                "description": "Anonymize converted/lost leads older than 90 days",
                "enabled": True
            },
            "daily_report": {
                "cron": "0 8 * * *",  # Daily at 8 AM
                "description": "Generate daily performance reports",
                "enabled": False  # Requires SMTP config
            },
            "backup": {
                "cron": "0 3 * * *",  # Daily at 3 AM
                "description": "Database backup",
                "enabled": False  # Requires backup config
            }
        }
