"""
Report Generation API Routes
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..middleware.auth import get_current_user
from ..models.user import User
from ..services.report_service import ReportService

router = APIRouter(tags=["Reports"])


@router.get("/leads/pdf")
async def generate_leads_pdf(
    start_date: str = Query(default=None),
    end_date: str = Query(default=None),
    branch_id: int = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate PDF report for leads
    Branch managers and IT admins only
    """
    if current_user.role not in ["branch_manager", "it_admin", "compliance"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Parse dates
    if not end_date:
        end = datetime.utcnow()
    else:
        end = datetime.fromisoformat(end_date)

    if not start_date:
        start = end - timedelta(days=30)
    else:
        start = datetime.fromisoformat(start_date)

    # Generate report
    report_service = ReportService()
    pdf_bytes = await report_service.generate_branch_report(
        db, start, end, branch_id, "pdf", current_user.email
    )

    filename = f"leads_report_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/leads/excel")
async def generate_leads_excel(
    start_date: str = Query(default=None),
    end_date: str = Query(default=None),
    branch_id: int = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate Excel report for leads
    """
    if current_user.role not in [
        "branch_manager",
        "sales_rep",
        "it_admin",
        "compliance",
    ]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Parse dates
    if not end_date:
        end = datetime.utcnow()
    else:
        end = datetime.fromisoformat(end_date)

    if not start_date:
        start = end - timedelta(days=30)
    else:
        start = datetime.fromisoformat(start_date)

    # Generate report
    report_service = ReportService()
    excel_bytes = await report_service.generate_branch_report(
        db, start, end, branch_id, "excel", current_user.email
    )

    filename = f"leads_report_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/performance/pdf")
async def generate_performance_pdf(
    start_date: str = Query(default=None),
    end_date: str = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate PDF performance report for branch managers
    """
    if current_user.role not in ["branch_manager", "it_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Parse dates
    if not end_date:
        end = datetime.utcnow()
    else:
        end = datetime.fromisoformat(end_date)

    if not start_date:
        start = end - timedelta(days=30)
    else:
        start = datetime.fromisoformat(start_date)

    # Generate report
    from ..services.report_service import PDFReportService

    pdf_service = PDFReportService()
    pdf_bytes = pdf_service.generate_performance_report(
        db, start, end, current_user.branch_id, current_user.email
    )

    filename = (
        f"performance_report_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.pdf"
    )

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/audit/excel")
async def generate_audit_excel(
    start_date: str = Query(default=None),
    end_date: str = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate Excel report for audit logs
    Compliance officers and IT admins only
    """
    if current_user.role not in ["compliance", "it_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Parse dates
    if not end_date:
        end = datetime.utcnow()
    else:
        end = datetime.fromisoformat(end_date)

    if not start_date:
        start = end - timedelta(days=30)
    else:
        start = datetime.fromisoformat(start_date)

    # Generate report
    report_service = ReportService()
    excel_bytes = await report_service.generate_audit_report(db, start, end, "excel")

    filename = f"audit_log_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# Import io at module level
import io
