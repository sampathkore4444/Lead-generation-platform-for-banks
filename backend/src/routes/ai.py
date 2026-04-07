"""
AI Routes
AI-powered endpoints for scoring, analytics, and chatbot
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from ..middleware.auth import get_current_user, get_optional_user
from ..models.user import User
from ..services.ai_service import ai_service, chatbot_service
from ..services.analytics_service import analytics_service


router = APIRouter()


# Request/Response Schemas
class LeadScoreRequest(BaseModel):
    lead_data: Dict[str, Any]


class LeadScoreResponse(BaseModel):
    lead_id: int
    score: int
    reason: str
    recommendation: str
    ai_insight: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class AnalyticsRequest(BaseModel):
    stats: Dict[str, Any]
    period: str = "daily"


# Lead Scoring Routes
@router.post("/score-lead", response_model=LeadScoreResponse)
async def score_lead(
    request: LeadScoreRequest, current_user: User = Depends(get_current_user)
):
    """Score a lead for conversion probability using AI"""
    result = await ai_service.score_lead(request.lead_data)

    return LeadScoreResponse(
        lead_id=request.lead_data.get("id", 0),
        score=result.get("score", 50),
        reason=result.get("reason", ""),
        recommendation=result.get("recommendation", "medium"),
    )


@router.post("/lead-insight")
async def get_lead_insight(
    lead_data: Dict[str, Any], current_user: User = Depends(get_current_user)
):
    """Get AI-generated insight about a lead"""
    insight = await ai_service.generate_insight(lead_data)
    return {"insight": insight}


@router.post("/predict-conversion")
async def predict_conversion(
    lead_data: Dict[str, Any], current_user: User = Depends(get_current_user)
):
    """Predict conversion timeline"""
    prediction = await ai_service.predict_conversion_time(lead_data)
    return {"prediction": prediction}


# Analytics Routes
@router.post("/generate-report")
async def generate_ai_report(
    request: AnalyticsRequest, current_user: User = Depends(get_current_user)
):
    """Generate AI-powered analytics report"""
    report = await analytics_service.generate_report(request.stats, request.period)
    return {"report": report}


@router.post("/predict-trend")
async def predict_trend(
    historical_data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user),
):
    """Predict future lead trends"""
    prediction = await analytics_service.predict_trend(historical_data)
    return prediction


@router.post("/analyze-performance")
async def analyze_rep_performance(
    rep_stats: List[Dict[str, Any]], current_user: User = Depends(get_current_user)
):
    """Analyze sales rep performance"""
    analysis = await analytics_service.analyze_rep_performance(rep_stats)
    return {"rep_analysis": analysis}


# Chatbot Routes
@router.post("/chatbot")
async def chatbot(
    request: ChatRequest, current_user: Optional[User] = Depends(get_optional_user)
):
    """AI Chatbot for customer queries"""
    if current_user:
        # Authenticated user
        response = await chatbot_service.chat(
            request.message, {"lead_name": current_user.full_name}
        )
    else:
        # Public access
        response = await chatbot_service.chat(request.message, {})

    return {"response": response}


@router.get("/product-info/{product}")
async def get_product_info(product: str):
    """Get product information from chatbot"""
    info = await chatbot_service.get_product_info(product)
    return {"info": info}
