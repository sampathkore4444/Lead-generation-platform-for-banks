"""
Smart Engines API Routes
Advanced AI/ML endpoints for STBank Lead Generation Platform
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..config.database import get_db
from ..middleware.auth import get_current_user
from ..models.user import User
from ..models.lead import Lead
from ..services.smart_engines_service import smart_engines

router = APIRouter(tags=["Smart Engines"])


# ==================== CREDIT SCORING ====================


@router.post("/credit-score")
async def calculate_credit_score(
    lead_id: int = Query(..., description="Lead ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculate credit score for a lead
    """
    # Get lead
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Build lead data
    lead_data = {
        "phone": lead.phone,
        "product": lead.product,
        "amount": float(lead.amount) if lead.amount else 0,
        "lao_id": lead.lao_id,
        "status": lead.status,
    }

    # Calculate score
    result = await smart_engines.calculate_credit_score(lead_data)

    return {
        "lead_id": lead_id,
        "credit_score": {
            "score": result.score,
            "rating": result.rating.value,
            "factors": result.factors,
            "recommendations": result.recommendations,
            "max_loan_amount": result.max_loan_amount,
            "suggested_rate": result.suggested_rate,
        },
    }


# ==================== PRODUCT RECOMMENDATIONS ====================


@router.post("/recommendations")
async def get_product_recommendations(
    lead_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get product recommendations for a lead
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_data = {
        "phone": lead.phone,
        "product": lead.product,
        "amount": float(lead.amount) if lead.amount else 0,
        "status": lead.status,
    }

    result = await smart_engines.recommend_products(lead_data)

    return {
        "lead_id": lead_id,
        "recommendations": {
            "products": result.products,
            "primary": result.primary_recommendation,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
        },
    }


# ==================== CHURN PREDICTION ====================


@router.post("/churn-prediction")
async def predict_churn(
    lead_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Predict churn probability for a lead
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Get interaction history (mock for now)
    interaction_history = []

    lead_data = {
        "phone": lead.phone,
        "product": lead.product,
        "amount": float(lead.amount) if lead.amount else 0,
        "status": lead.status,
        "last_contact": lead.updated_at,
        "response_rate": 0.7,  # Mock
    }

    result = await smart_engines.predict_churn(lead_data, interaction_history)

    return {
        "lead_id": lead_id,
        "churn_prediction": {
            "probability": result.churn_probability,
            "risk_level": result.risk_level,
            "factors": result.factors,
            "retention_suggestions": result.retention_suggestions,
        },
    }


# ==================== OPTIMAL CONTACT TIME ====================


@router.post("/optimal-contact-time")
async def get_optimal_contact_time(
    lead_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Predict optimal contact time for a lead
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_data = {
        "phone": lead.phone,
        "product": lead.product,
        "preferred_time": lead.preferred_time,
    }

    result = await smart_engines.predict_optimal_contact_time(lead_data)

    return {
        "lead_id": lead_id,
        "optimal_time": {
            "best_time": result.best_time,
            "best_day": result.best_day,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
        },
    }


# ==================== VOICE ANALYTICS ====================


@router.post("/voice-analytics")
async def analyze_voice_call(
    call_transcript: str,
    agent_id: int = Query(...),
    call_duration: int = Query(default=300),
    interruptions: int = Query(default=0),
    wpm: int = Query(default=150),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze voice call recording/transcript
    """
    metadata = {
        "call_duration": call_duration,
        "interruptions": interruptions,
        "wpm": wpm,
        "agent_id": agent_id,
    }

    result = await smart_engines.analyze_voice_call(call_transcript, metadata)

    return {
        "call_analysis": {
            "sentiment": {
                "score": result.sentiment_score,
                "label": result.sentiment_label,
            },
            "keywords": result.keywords,
            "topics": result.topics,
            "talk_ratio": result.talk_ratio,
            "interruption_count": result.interruption_count,
            "speaking_pace": result.speaking_pace,
            "emotions": result.emotions,
            "compliance_mentions": result.compliance_mentions,
        }
    }


# ==================== CONVERSATION INTELLIGENCE ====================


@router.post("/conversation-intelligence")
async def analyze_conversation(
    lead_id: int = Query(...),
    transcript: str = Query(..., description="Call transcript"),
    agent_notes: str = Query(default="", description="Agent notes"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get conversation intelligence for a lead interaction
    """
    result = await smart_engines.analyze_conversation(transcript, agent_notes)

    return {
        "lead_id": lead_id,
        "intelligence": {
            "summary": result.call_summary,
            "action_items": result.action_items,
            "next_steps": result.next_steps,
            "interest_level": result.lead_interest_level,
            "qualification_status": result.qualification_status,
            "objections": result.key_objections,
            "closing_signals": result.closing_signals,
            "recommended_action": result.recommended_next_action,
        },
    }


# ==================== RISK ASSESSMENT ====================


@router.post("/risk-assessment")
async def assess_risk(
    lead_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Comprehensive risk assessment for a lead
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Get credit score
    lead_data = {
        "phone": lead.phone,
        "product": lead.product,
        "amount": float(lead.amount) if lead.amount else 0,
        "lao_id": lead.lao_id,
    }

    credit_result = await smart_engines.calculate_credit_score(lead_data)

    # Mock fraud indicators
    fraud_indicators = []
    if lead.phone and not lead.phone.startswith("20"):
        fraud_indicators.append("Unusual phone format")

    result = await smart_engines.assess_risk(
        lead_data, credit_result.score, fraud_indicators
    )

    return {
        "lead_id": lead_id,
        "risk_assessment": {
            "overall_score": result.overall_risk_score,
            "risk_level": result.risk_level.value,
            "factors": result.risk_factors,
            "mitigations": result.mitigation_suggestions,
            "fraud_indicators": result.fraud_indicators,
            "credit_considerations": result.credit_considerations,
        },
    }


# ==================== AUTO-SCHEDULER ====================


@router.post("/auto-schedule")
async def auto_schedule(
    lead_id: int = Query(...),
    priority: str = Query(default="normal"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate automatic schedule recommendation
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Mock agent availability
    agent_availability = []

    lead_data = {
        "phone": lead.phone,
        "product": lead.product,
        "preferred_time": lead.preferred_time,
    }

    result = await smart_engines.generate_schedule_recommendation(
        lead_data, agent_availability, priority
    )

    return {
        "lead_id": lead_id,
        "schedule": {
            "scheduled_time": result.scheduled_time.isoformat(),
            "duration_minutes": result.duration_minutes,
            "channel": result.channel,
            "priority": result.priority,
            "reason": result.reason,
        },
    }


# ==================== COMPREHENSIVE ANALYSIS ====================


@router.post("/comprehensive-analysis")
async def comprehensive_analysis(
    lead_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run all smart engines on a lead for comprehensive analysis
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_data = {
        "phone": lead.phone,
        "product": lead.product,
        "amount": float(lead.amount) if lead.amount else 0,
        "lao_id": lead.lao_id,
        "preferred_time": lead.preferred_time,
        "status": lead.status,
        "last_contact": lead.updated_at,
    }

    # Run all analyses in parallel
    credit = await smart_engines.calculate_credit_score(lead_data)
    recommendations = await smart_engines.recommend_products(lead_data)
    churn = await smart_engines.predict_churn(lead_data, [])
    contact_time = await smart_engines.predict_optimal_contact_time(lead_data)
    risk = await smart_engines.assess_risk(lead_data, credit.score, [])
    schedule = await smart_engines.generate_schedule_recommendation(
        lead_data, [], "normal"
    )

    return {
        "lead_id": lead_id,
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "credit_score": {
            "score": credit.score,
            "rating": credit.rating.value,
            "max_loan": credit.max_loan_amount,
            "rate": credit.suggested_rate,
        },
        "recommendations": {
            "products": recommendations.products,
            "primary": recommendations.primary_recommendation,
        },
        "churn_prediction": {
            "probability": churn.churn_probability,
            "risk_level": churn.risk_level,
        },
        "optimal_contact": {
            "time": contact_time.best_time,
            "day": contact_time.best_day,
        },
        "risk_assessment": {
            "score": risk.overall_risk_score,
            "level": risk.risk_level.value,
        },
        "schedule": {
            "suggested_time": schedule.scheduled_time.isoformat(),
            "channel": schedule.channel,
            "duration": schedule.duration_minutes,
        },
    }


from datetime import datetime
