"""
Admin API Routes - Anonymization & System Management
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.middleware.auth import get_current_user
from backend.src.models.user import User
from backend.src.services.anonymization_service import AnonymizationService, ScheduledJobService

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


# ==================== ANONYMIZATION ====================

@router.get("/anonymization/stats")
async def get_anonymization_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get anonymization statistics
    IT admins and compliance officers only
    """
    if current_user.role not in ["it_admin", "compliance"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return AnonymizationService.get_anonymization_stats(db)


@router.post("/anonymization/run")
async def run_anonymization(
    dry_run: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run anonymization job
    Default is dry_run to preview affected records
    Set dry_run=false to execute
    
    IT admins only
    """
    if current_user.role != "it_admin":
        raise HTTPException(status_code=403, detail="IT admin access required")
    
    result = AnonymizationService.run_anonymization_job(db, dry_run=dry_run)
    
    if dry_run:
        return {
            **result,
            "warning": "This was a dry run. Set dry_run=false to execute."
        }
    
    return result


@router.get("/anonymization/retention")
async def get_retention_info():
    """
    Get audit log retention policy information
    """
    return AnonymizationService.get_audit_log_retention_info()


@router.post("/anonymization/restore/{lead_id}")
async def restore_anonymized_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Attempt to restore an anonymized lead
    Note: Requires manual data recovery
    
    IT admins only
    """
    if current_user.role != "it_admin":
        raise HTTPException(status_code=403, detail="IT admin access required")
    
    success = AnonymizationService.restore_lead(db, lead_id, current_user.id)
    
    if success:
        return {"message": "Restore request logged. Manual data recovery required."}
    else:
        raise HTTPException(status_code=404, detail="Lead not found or not anonymized")


# ==================== SCHEDULED JOBS ====================

@router.get("/jobs/schedule")
async def get_job_schedule(
    current_user: User = Depends(get_current_user)
):
    """
    Get configured job schedules
    IT admins only
    """
    if current_user.role != "it_admin":
        raise HTTPException(status_code=403, detail="IT admin access required")
    
    return ScheduledJobService.get_job_schedule()


@router.post("/jobs/run")
async def run_scheduled_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger scheduled jobs
    IT admins only
    """
    if current_user.role != "it_admin":
        raise HTTPException(status_code=403, detail="IT admin access required")
    
    result = await ScheduledJobService.check_and_run_scheduled_jobs(db)
    
    return {
        "message": "Scheduled jobs executed",
        "results": result
    }


# ==================== LDAP CONFIG ====================

@router.get("/ldap/config")
async def get_ldap_config(
    current_user: User = Depends(get_current_user)
):
    """
    Get LDAP configuration status
    IT admins only
    """
    if current_user.role != "it_admin":
        raise HTTPException(status_code=403, detail="IT admin access required")
    
    from backend.src.services.ldap_service import LDAPService
    from backend.src.config.settings import settings
    
    ldap_service = LDAPService({
        "LDAP_ENABLED": settings.LDAP_ENABLED
    })
    
    return {
        "enabled": settings.LDAP_ENABLED,
        "server": settings.LDAP_SERVER if settings.LDAP_ENABLED else None,
        "base_dn": settings.LDAP_BASE_DN if settings.LDAP_ENABLED else None
    }


@router.post("/ldap/test")
async def test_ldap_connection(
    username: str,
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test LDAP connection with credentials
    IT admins only
    """
    if current_user.role != "it_admin":
        raise HTTPException(status_code=403, detail="IT admin access required")
    
    from backend.src.services.ldap_service import LDAPService
    from backend.src.config.settings import settings
    
    ldap_service = LDAPService({
        "LDAP_SERVER": settings.LDAP_SERVER,
        "LDAP_BASE_DN": settings.LDAP_BASE_DN,
        "LDAP_USER_DN": settings.LDAP_USER_DN,
        "LDAP_PASSWORD": settings.LDAP_PASSWORD,
        "LDAP_USE_SSL": settings.LDAP_USE_SSL,
        "LDAP_ENABLED": True  # Enable for testing
    })
    
    result = ldap_service.authenticate(username, password)
    
    if result:
        return {
            "success": True,
            "user": {
                "username": result.username,
                "email": result.email,
                "display_name": result.display_name,
                "department": result.department,
                "role": ldap_service.get_user_role(result)
            }
        }
    else:
        return {
            "success": False,
            "message": "Authentication failed"
        }


# ==================== SYSTEM INFO ====================

@router.get("/system/info")
async def get_system_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get system information
    IT admins only
    """
    if current_user.role != "it_admin":
        raise HTTPException(status_code=403, detail="IT admin access required")
    
    from backend.src.config.settings import settings
    
    return {
        "app_name": "STBank Laos Lead Generation Platform",
        "version": "1.0.0",
        "environment": "on-premise",
        "features": {
            "ldap": settings.LDAP_ENABLED,
            "mfa": True,
            "ai": settings.AI_SCORING_ENABLED,
            "chatbot": settings.AI_CHATBOT_ENABLED,
            "voice": True,
            "whatsapp": settings.WHATSAPP_ENABLED,
            "line": settings.LINE_ENABLED
        },
        "data_residency": "Laos (on-premise)",
        "audit_retention_years": 7
    }
