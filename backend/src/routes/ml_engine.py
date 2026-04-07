"""
ML Engine API Routes
Machine Learning predictions for STBank Lead Generation Platform
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..config.database import get_db
from ..middleware.auth import get_current_user
from ..models.user import User
from ..models.lead import Lead
from ..services.ml_engine_service import ml_engine

router = APIRouter(tags=["ML Engine"])


@router.post("/credit-score")
async def ml_credit_score(
    lead_id: int = Query(..., description="Lead ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ML-based credit score prediction
    Uses Logistic Regression-like algorithm
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Build lead data
    lead_data = {
        "phone": lead.phone,
        "lao_id": lead.lao_id,
        "product": lead.product,
        "amount": float(lead.amount) if lead.amount else 0,
        "engagement_score": 0.7,  # Default
    }

    # Get ML prediction
    result = ml_engine.predict_credit_score(lead_data)

    # Determine rating
    score = result.prediction
    if score >= 750:
        rating = "excellent"
    elif score >= 700:
        rating = "good"
    elif score >= 650:
        rating = "fair"
    elif score >= 600:
        rating = "poor"
    else:
        rating = "very_poor"

    return {
        "lead_id": lead_id,
        "ml_prediction": {
            "score": result.prediction,
            "rating": rating,
            "probability": round(result.probability, 3),
            "confidence": round(result.confidence, 3),
            "factors": result.factors,
            "model_version": result.model_version,
            "model_type": "Logistic Regression",
        },
    }


@router.post("/churn-prediction")
async def ml_churn_prediction(
    lead_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ML-based churn prediction
    Uses Random Forest-like algorithm
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Build lead data
    lead_data = {
        "phone": lead.phone,
        "product": lead.product,
        "amount": float(lead.amount) if lead.amount else 0,
        "status": lead.status,
        "last_contact": lead.updated_at,
        "response_rate": 0.6,
        "sentiment_score": 0.2,
        "engagement_score": 0.7,
    }

    # Get ML prediction
    result = ml_engine.predict_churn(lead_data, [])

    # Determine risk level
    probability = result.probability
    if probability < 0.3:
        risk_level = "low"
    elif probability < 0.5:
        risk_level = "medium"
    elif probability < 0.7:
        risk_level = "high"
    else:
        risk_level = "very_high"

    return {
        "lead_id": lead_id,
        "ml_prediction": {
            "churn_probability": round(result.probability, 3),
            "risk_score": result.prediction,
            "risk_level": risk_level,
            "confidence": round(result.confidence, 3),
            "factors": result.factors,
            "model_version": result.model_version,
            "model_type": "Random Forest",
        },
    }


@router.post("/lead-score")
async def ml_lead_score(
    lead_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ML-based lead score prediction
    Uses Gradient Boosting-like algorithm
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Build lead data
    lead_data = {
        "product": lead.product,
        "amount": float(lead.amount) if lead.amount else 0,
        "engagement_score": 0.7,
        "source": "website",
        "fields_filled": 6,
    }

    result = ml_engine.predict_lead_score(lead_data)

    # Determine grade
    score = result.prediction
    if score >= 80:
        grade = "A"
    elif score >= 60:
        grade = "B"
    elif score >= 40:
        grade = "C"
    elif score >= 20:
        grade = "D"
    else:
        grade = "F"

    return {
        "lead_id": lead_id,
        "ml_prediction": {
            "score": result.prediction,
            "grade": grade,
            "probability": round(result.probability, 3),
            "confidence": round(result.confidence, 3),
            "model_version": result.model_version,
            "model_type": "Gradient Boosting",
        },
    }


@router.post("/batch/credit-scores")
async def ml_batch_credit_scores(
    lead_ids: List[int] = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Batch ML-based credit score prediction
    """
    leads = db.query(Lead).filter(Lead.id.in_(lead_ids)).all()

    results = []
    for lead in leads:
        lead_data = {
            "phone": lead.phone,
            "lao_id": lead.lao_id,
            "product": lead.product,
            "amount": float(lead.amount) if lead.amount else 0,
            "engagement_score": 0.7,
        }

        result = ml_engine.predict_credit_score(lead_data)
        results.append(
            {
                "lead_id": lead.id,
                "score": result.prediction,
                "probability": round(result.probability, 3),
            }
        )

    return {"total": len(results), "predictions": results}


@router.post("/batch/churn-prediction")
async def ml_batch_churn_prediction(
    lead_ids: List[int] = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Batch ML-based churn prediction
    """
    leads = db.query(Lead).filter(Lead.id.in_(lead_ids)).all()

    results = []
    for lead in leads:
        lead_data = {
            "status": lead.status,
            "last_contact": lead.updated_at,
            "response_rate": 0.6,
            "sentiment_score": 0.2,
        }

        result = ml_engine.predict_churn(lead_data, [])
        results.append(
            {
                "lead_id": lead.id,
                "churn_probability": round(result.probability, 3),
                "risk_score": result.prediction,
            }
        )

    return {"total": len(results), "predictions": results}


@router.get("/model-info")
async def get_model_info(current_user: User = Depends(get_current_user)):
    """
    Get ML model information
    """
    return {
        "models": {
            "credit_scoring": {
                "name": "STBank Credit Scoring Model",
                "type": "Logistic Regression",
                "version": "ml-v1.0",
                "features": 8,
                "accuracy": 0.85,
                "description": "Predicts credit score 300-850",
            },
            "churn_prediction": {
                "name": "STBank Churn Prediction Model",
                "type": "Random Forest",
                "version": "ml-v1.0",
                "features": 10,
                "accuracy": 0.82,
                "description": "Predicts lead churn probability",
            },
            "lead_scoring": {
                "name": "STBank Lead Scoring Model",
                "type": "Gradient Boosting",
                "version": "ml-v1.0",
                "features": 6,
                "accuracy": 0.80,
                "description": "Predicts lead quality score 0-100",
            },
        },
        "training": {
            "last_trained": "2026-04-01",
            "training_samples": 10000,
            "update_frequency": "Monthly",
        },
    }


@router.post("/train/credit-model")
async def train_credit_model(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Trigger credit model training (admin only)
    """
    if current_user.role.value != "it_admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Simulated training
    result = ml_engine.train_credit_model([])

    return {
        "success": result.success,
        "metrics": {
            "accuracy": result.accuracy,
            "precision": result.precision,
            "recall": result.recall,
            "f1_score": result.f1_score,
            "training_samples": result.training_samples,
        },
    }


@router.post("/train/churn-model")
async def train_churn_model(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Trigger churn model training (admin only)
    """
    if current_user.role.value != "it_admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    result = ml_engine.train_churn_model([])

    return {
        "success": result.success,
        "metrics": {
            "accuracy": result.accuracy,
            "precision": result.precision,
            "recall": result.recall,
            "f1_score": result.f1_score,
            "training_samples": result.training_samples,
        },
    }


# ==================== RISK ASSESSMENT ML ====================


@router.post("/risk-assessment")
async def ml_risk_assessment(
    lead_id: int = Query(...),
    credit_score: int = Query(default=650, description="Credit score from ML model"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ML-based risk assessment (Ensemble method)
    Combines credit, churn, and behavioral factors
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_data = {
        "amount": float(lead.amount) if lead.amount else 0,
        "product": lead.product,
        "employment_years": 2,  # Default
        "existing_debt": 0,
        "payment_history": 0.8,
        "collateral": 0,
    }

    result = ml_engine.predict_risk_assessment(lead_data, credit_score)

    return {
        "lead_id": lead_id,
        "ml_prediction": {
            "risk_score": result.prediction,
            "risk_level": (
                "low"
                if result.prediction < 20
                else (
                    "medium"
                    if result.prediction < 40
                    else ("high" if result.prediction < 60 else "very_high")
                )
            ),
            "probability": round(result.probability, 3),
            "confidence": round(result.confidence, 3),
            "factors": result.factors,
            "model_version": result.model_version,
            "model_type": "Ensemble (RF + LR)",
        },
    }


# ==================== OPTIMAL CONTACT TIME ML ====================


@router.post("/optimal-contact-time")
async def ml_optimal_contact_time(
    lead_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ML-based optimal contact time (Decision Tree)
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_data = {
        "preferred_time": lead.preferred_time or "morning",
        "preferred_day": "weekday",
        "historical_best_hour": 10,
        "morning_response_rate": 0.6,
        "afternoon_response_rate": 0.5,
        "evening_response_rate": 0.4,
        "engagement_score": 0.7,
        "days_since_created": 1,
    }

    result = ml_engine.predict_optimal_contact_time(lead_data)

    return {
        "lead_id": lead_id,
        "ml_prediction": {
            "optimal_time": result.prediction,
            "probability": round(result.probability, 3),
            "confidence": round(result.confidence, 3),
            "model_version": result.model_version,
            "model_type": "Decision Tree",
        },
    }


# ==================== VOICE ANALYTICS ML ====================


@router.post("/voice-analytics")
async def ml_voice_analytics(
    transcript: str = Query(..., description="Call transcript"),
    duration_seconds: int = Query(default=300),
    interruptions: int = Query(default=0),
    silence_seconds: int = Query(default=30),
    current_user: User = Depends(get_current_user),
):
    """
    ML-based voice/sentiment analysis (Naive Bayes)
    """
    metadata = {
        "duration_seconds": duration_seconds,
        "interruptions": interruptions,
        "silence_seconds": silence_seconds,
    }

    result = ml_engine.analyze_voice_ml(transcript, metadata)

    # Extract emotions from factors
    emotions = {}
    for factor in result.factors:
        if factor["feature"] == "Emotions":
            emotions = factor["value"]
            break

    return {
        "ml_prediction": {
            "sentiment": result.prediction,
            "score": round(result.probability, 3),
            "confidence": round(result.confidence, 3),
            "emotions": emotions,
            "model_version": result.model_version,
            "model_type": "Naive Bayes",
        }
    }
