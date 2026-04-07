"""
API Router
Main router that combines all API routes
"""
from fastapi import APIRouter

from . import auth, leads


# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])