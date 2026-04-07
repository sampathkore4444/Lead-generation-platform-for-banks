"""
API Router
Main router that combines all API routes
"""

from fastapi import APIRouter

from . import (
    auth,
    leads,
    ai,
    integrations,
    mfa,
    reports,
    admin,
    smart_engines,
    ml_engine,
)


# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(
    integrations.router, prefix="/integrations", tags=["Integrations"]
)
api_router.include_router(mfa.router, prefix="/mfa", tags=["MFA & Captcha"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(
    smart_engines.router, prefix="/smart-engines", tags=["Smart Engines"]
)
api_router.include_router(ml_engine.router, prefix="/ml", tags=["ML Engine"])
