"""
Integration Routes
Voice, WhatsApp/Line, Sentiment, Fraud detection
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any

from ..middleware.auth import get_current_user
from ..models.user import User
from ..services.integration_service import (
    voice_service,
    whatsapp_service,
    sentiment_service,
    fraud_detection,
)


router = APIRouter()


# Request/Response Schemas
class CallRequest(BaseModel):
    phone: str
    lead_id: int


class WhatsAppRequest(BaseModel):
    phone: str
    message: Optional[str] = None
    template: Optional[str] = None
    params: Optional[Dict[str, str]] = None


class SentimentRequest(BaseModel):
    text: str


class FraudCheckRequest(BaseModel):
    lead_data: Dict[str, Any]
    ip_address: Optional[str] = None


# Voice Routes
@router.post("/call/initiate")
async def initiate_call(
    request: CallRequest, current_user: User = Depends(get_current_user)
):
    """Initiate outbound call to lead"""
    result = await voice_service.initiate_call(request.phone, request.lead_id)
    return result


@router.get("/call/{call_id}")
async def get_call_status(call_id: str, current_user: User = Depends(get_current_user)):
    """Get call status"""
    result = await voice_service.get_call_status(call_id)
    return result


# WhatsApp/Line Routes
@router.post("/whatsapp/send")
async def send_whatsapp(
    request: WhatsAppRequest, current_user: User = Depends(get_current_user)
):
    """Send WhatsApp message"""
    if request.template:
        result = await whatsapp_service.send_template(
            request.phone, request.template, request.params or {}
        )
    else:
        result = await whatsapp_service.send_whatsapp(
            request.phone, request.message or ""
        )
    return result


@router.post("/line/send")
async def send_line(
    request: WhatsAppRequest, current_user: User = Depends(get_current_user)
):
    """Send LINE message"""
    result = await whatsapp_service.send_line(request.phone, request.message or "")
    return result


# Sentiment Routes
@router.post("/sentiment")
async def analyze_sentiment(
    request: SentimentRequest, current_user: User = Depends(get_current_user)
):
    """Analyze text sentiment"""
    result = await sentiment_service.analyze_sentiment(request.text)
    return result


@router.post("/call/analyze")
async def analyze_call(
    recording_url: str, current_user: User = Depends(get_current_user)
):
    """Analyze call recording"""
    result = await sentiment_service.analyze_call_recording(recording_url)
    return result


# Fraud Detection Routes
@router.post("/fraud/check")
async def check_fraud(
    request: FraudCheckRequest, current_user: User = Depends(get_current_user)
):
    """Check lead for fraud"""
    result = await fraud_detection.check_fraud(request.lead_data)

    if request.ip_address:
        ip_check = await fraud_detection.check_ip_fraud(request.ip_address)
        result["ip_analysis"] = ip_check

    return result


@router.get("/fraud/risk-levels")
async def get_risk_levels():
    """Get fraud risk level descriptions"""
    return {
        "low": "Lead approved automatically",
        "medium": "Additional verification required",
        "high": "Manual review required before processing",
    }
