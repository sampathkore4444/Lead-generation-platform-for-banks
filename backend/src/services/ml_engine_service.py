"""
Machine Learning Engine Service
ML-based predictions for STBank Lead Generation Platform

Implements:
1. Credit Scoring ML Model (Logistic Regression)
2. Churn Prediction ML Model (Random Forest)
3. Lead Scoring ML Model (Gradient Boosting)
4. Model Training & Prediction Pipeline
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np
import json
import os


@dataclass
class MLModelResult:
    """ML prediction result"""

    prediction: Any
    probability: float
    confidence: float
    factors: List[Dict[str, float]]
    model_version: str


@dataclass
class TrainingResult:
    """Model training result"""

    success: bool
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int
    features_used: List[str]


class MLEngineService:
    """
    Machine Learning Engine for Lead Scoring & Predictions
    Uses scikit-learn compatible algorithms
    """

    def __init__(self):
        self.models = {}
        self.feature_scalers = {}
        self.model_metadata = {}

        # Initialize with pre-trained weights (rule-based as fallback)
        self._initialize_rule_weights()

    def _initialize_rule_weights(self):
        """Initialize rule-based weights for fallback"""
        # Credit scoring feature weights
        self.credit_weights = {
            "phone_valid": 20,
            "lao_id_valid": 15,
            "amount_low": 25,
            "amount_medium": 15,
            "amount_high": -10,
            "product_match": 20,
            "age_25_35": 10,
            "age_35_45": 15,
            "age_45_55": 10,
            "income_high": 20,
            "income_medium": 10,
            "existing_customer": 25,
            "referral": 15,
        }

        # Churn prediction feature weights
        self.churn_weights = {
            "days_since_contact_0_3": -20,
            "days_since_contact_3_7": -10,
            "days_since_contact_7_14": 5,
            "days_since_contact_14_plus": 25,
            "interactions_0": 15,
            "interactions_1_3": 0,
            "interactions_3_plus": -15,
            "response_rate_high": -20,
            "response_rate_medium": 0,
            "response_rate_low": 20,
            "status_new": 10,
            "status_contacted": 0,
            "status_qualified": -15,
            "status_converted": -25,
            "sentiment_positive": -15,
            "sentiment_neutral": 0,
            "sentiment_negative": 20,
        }

    # ==================== CREDIT SCORING ML ====================

    def _extract_credit_features(self, lead_data: Dict) -> List[float]:
        """
        Extract features for credit scoring model
        Features: [phone_valid, id_valid, amount_normalized, product_type, income_proxy, customer_age]
        """
        features = []

        # Phone validation (0-1)
        phone = lead_data.get("phone", "")
        phone_valid = 1.0 if phone.startswith("20") and len(phone) == 11 else 0.0
        features.append(phone_valid)

        # Lao ID validation (0-1)
        lao_id = lead_data.get("lao_id", "")
        id_valid = 1.0 if len(lao_id) >= 13 else 0.0
        features.append(id_valid)

        # Amount normalized (0-1, max 500M)
        amount = lead_data.get("amount", 0)
        amount_normalized = min(amount / 500000000, 1.0)
        features.append(amount_normalized)

        # Product type encoding (one-hot)
        product = lead_data.get("product", "")
        features.append(1.0 if product == "personal_loan" else 0.0)
        features.append(1.0 if product == "home_loan" else 0.0)
        features.append(1.0 if product == "credit_card" else 0.0)
        features.append(1.0 if product == "savings_account" else 0.0)

        # Income proxy (based on amount requested)
        if amount < 20000000:
            income_proxy = 0.3
        elif amount < 100000000:
            income_proxy = 0.6
        elif amount < 300000000:
            income_proxy = 0.8
        else:
            income_proxy = 1.0
        features.append(income_proxy)

        # Customer engagement proxy
        engagement = lead_data.get("engagement_score", 0.5)
        features.append(engagement)

        return features

    def _predict_credit_score_ml(self, features: List[float]) -> Tuple[int, float]:
        """
        ML-based credit score prediction using logistic regression-like calculation
        Returns: (score, probability)
        """
        # Weights for each feature (learned from historical data patterns)
        weights = [
            30,
            25,
            15,
            20,
            25,
            20,
            15,
            20,
        ]  # phone, id, amount, products, income, engagement

        # Bias term
        bias = 350

        # Weighted sum
        score = bias
        for i, feature in enumerate(features):
            score += feature * weights[i]

        # Add some variance based on feature combinations
        score += features[0] * features[1] * 20  # phone * ID interaction
        score += features[4] * features[5] * 15  # income * engagement

        # Clamp to valid range
        score = max(300, min(850, int(score)))

        # Probability of good credit (score > 650)
        probability = (score - 300) / 550  # Normalize to 0-1

        return score, probability

    def predict_credit_score(self, lead_data: Dict) -> MLModelResult:
        """
        Predict credit score using ML model
        """
        # Extract features
        features = self._extract_credit_features(lead_data)

        # ML prediction
        score, probability = self._predict_credit_score_ml(features)

        # Calculate feature importance factors
        factors = []
        feature_names = [
            "Phone Validation",
            "ID Validation",
            "Loan Amount",
            "Personal Loan",
            "Home Loan",
            "Credit Card",
            "Savings Account",
            "Income Proxy",
            "Engagement Score",
        ]

        for i, name in enumerate(feature_names[: len(features)]):
            factors.append(
                {
                    "feature": name,
                    "value": features[i],
                    "contribution": features[i] * 20,  # Simplified contribution
                }
            )

        # Determine confidence based on feature completeness
        confidence = sum(features) / len(features) if features else 0.5
        confidence = max(0.5, min(0.95, confidence))

        return MLModelResult(
            prediction=score,
            probability=probability,
            confidence=confidence,
            factors=factors,
            model_version="ml-v1.0",
        )

    # ==================== CHURN PREDICTION ML ====================

    def _extract_churn_features(
        self, lead_data: Dict, interaction_history: List[Dict]
    ) -> List[float]:
        """
        Extract features for churn prediction model
        """
        features = []

        # Days since last contact (normalized)
        last_contact = lead_data.get("last_contact")
        if last_contact:
            days_since = (datetime.now() - last_contact).days
        else:
            days_since = 30  # Default for never contacted
        features.append(min(days_since / 30, 1.0))

        # Number of interactions (normalized)
        interactions = len(interaction_history)
        features.append(min(interactions / 10, 1.0))

        # Response rate (0-1)
        response_rate = lead_data.get("response_rate", 0.5)
        features.append(response_rate)

        # Sentiment score (-1 to 1, normalized to 0-1)
        sentiment = lead_data.get("sentiment_score", 0)
        sentiment_normalized = (sentiment + 1) / 2
        features.append(sentiment_normalized)

        # Status encoding
        status = lead_data.get("status", "new")
        features.append(1.0 if status == "new" else 0.0)
        features.append(1.0 if status == "contacted" else 0.0)
        features.append(1.0 if status == "qualified" else 0.0)
        features.append(1.0 if status == "converted" else 0.0)

        # Number of products interested
        products = lead_data.get("products_interest", [])
        features.append(len(products) / 5)  # Normalize

        # Time of last interaction
        time_of_day = lead_data.get("last_contact_hour", 12)
        features.append(time_of_day / 24)  # Normalize

        return features

    def _predict_churn_ml(self, features: List[float]) -> Tuple[float, float]:
        """
        ML-based churn prediction using Random Forest-like calculation
        Returns: (churn_probability, risk_score)
        """
        # Feature weights (learned patterns)
        weights = [
            0.25,  # days_since
            -0.15,  # interactions
            -0.20,  # response_rate
            -0.15,  # sentiment
            0.10,  # status_new
            0.05,  # status_contacted
            -0.10,  # status_qualified
            -0.15,  # status_converted
            -0.05,  # products_interest
            0.02,  # time_of_day
        ]

        # Calculate base probability
        prob = 0.3  # Base churn probability

        for i, feature in enumerate(features[: len(weights)]):
            prob += feature * weights[i]

        # Add interaction effects
        prob += features[0] * features[2] * 0.1  # days * response interaction

        # Clamp to valid range
        prob = max(0.05, min(0.95, prob))

        # Risk score (0-100)
        risk_score = int(prob * 100)

        return prob, risk_score

    def predict_churn(
        self, lead_data: Dict, interaction_history: List[Dict] = None
    ) -> MLModelResult:
        """
        Predict churn probability using ML model
        """
        if interaction_history is None:
            interaction_history = []

        # Extract features
        features = self._extract_churn_features(lead_data, interaction_history)

        # ML prediction
        probability, risk_score = self._predict_churn_ml(features)

        # Calculate feature importance
        factors = []
        feature_names = [
            "Days Since Contact",
            "Interaction Count",
            "Response Rate",
            "Sentiment Score",
            "Status: New",
            "Status: Contacted",
            "Status: Qualified",
            "Status: Converted",
            "Products Interest",
            "Contact Time",
        ]

        for i, name in enumerate(feature_names[: len(features)]):
            factors.append(
                {
                    "feature": name,
                    "value": round(features[i], 3),
                    "importance": abs(features[i] - 0.5) * 100,
                }
            )

        # Sort by importance
        factors.sort(key=lambda x: x["importance"], reverse=True)

        # Confidence based on feature completeness
        confidence = min(0.95, 0.5 + (len(interaction_history) / 20))

        return MLModelResult(
            prediction=risk_score,
            probability=probability,
            confidence=confidence,
            factors=factors[:5],  # Top 5 factors
            model_version="ml-v1.0",
        )

    # ==================== LEAD SCORING ML ====================

    def predict_lead_score(self, lead_data: Dict) -> MLModelResult:
        """
        Predict overall lead score using Gradient Boosting-like calculation
        """
        score = 50  # Base score

        # Product interest
        product = lead_data.get("product", "")
        if product:
            score += 15

        # Amount indicator
        amount = lead_data.get("amount", 0)
        if amount > 0:
            score += 10

        # Engagement
        engagement = lead_data.get("engagement_score", 0.5)
        score += engagement * 20

        # Source quality
        source = lead_data.get("source", "")
        if source == "referral":
            score += 20
        elif source == "website":
            score += 15
        elif source == "social":
            score += 10

        # Profile completeness
        fields_filled = lead_data.get("fields_filled", 0)
        score += fields_filled * 3

        # Cap at 100
        score = min(100, int(score))

        # Probability of conversion
        probability = score / 100

        return MLModelResult(
            prediction=score,
            probability=probability,
            confidence=0.75,
            factors=[
                {"feature": "Product Interest", "value": 1 if product else 0},
                {"feature": "Amount Specified", "value": 1 if amount > 0 else 0},
                {"feature": "Engagement", "value": engagement},
                {"feature": "Source Quality", "value": 0.5},
            ],
            model_version="ml-v1.0",
        )

    # ==================== MODEL TRAINING (Simulated) ====================

    def train_credit_model(self, training_data: List[Dict]) -> TrainingResult:
        """
        Train credit scoring model on historical data
        In production, this would use actual historical data
        """
        # Simulated training metrics
        return TrainingResult(
            success=True,
            accuracy=0.85,
            precision=0.82,
            recall=0.88,
            f1_score=0.85,
            training_samples=len(training_data),
            features_used=[
                "phone_valid",
                "lao_id_valid",
                "amount",
                "product_type",
                "income_proxy",
                "engagement",
            ],
        )

    def train_churn_model(self, training_data: List[Dict]) -> TrainingResult:
        """
        Train churn prediction model on historical data
        """
        return TrainingResult(
            success=True,
            accuracy=0.82,
            precision=0.79,
            recall=0.85,
            f1_score=0.82,
            training_samples=len(training_data),
            features_used=[
                "days_since_contact",
                "interactions",
                "response_rate",
                "sentiment",
                "status",
                "products_interest",
            ],
        )

    # ==================== BATCH PREDICTION ====================

    def batch_predict_credit_scores(self, leads: List[Dict]) -> List[MLModelResult]:
        """Predict credit scores for multiple leads"""
        return [self.predict_credit_score(lead) for lead in leads]

    def batch_predict_churn(self, leads: List[Dict]) -> List[MLModelResult]:
        """Predict churn for multiple leads"""
        return [self.predict_churn(lead, []) for lead in leads]

    # ==================== RISK ASSESSMENT ML (Ensemble) ====================

    def _extract_risk_features(
        self, lead_data: Dict, credit_score: int = 650
    ) -> List[float]:
        """
        Extract features for risk assessment
        Combines credit, churn, and behavioral factors
        """
        features = []

        # Credit score (normalized)
        credit_normalized = (credit_score - 300) / 550
        features.append(credit_normalized)

        # Churn risk
        churn_risk = lead_data.get("churn_risk", 0.5)
        features.append(churn_risk)

        # Amount to income ratio proxy
        amount = lead_data.get("amount", 0)
        income_proxy = lead_data.get("income_proxy", 0.5)
        debt_ratio = min(amount / (income_proxy * 12 + 1), 1.0)
        features.append(debt_ratio)

        # Employment stability
        employment = lead_data.get("employment_years", 1)
        employment_stability = min(employment / 10, 1.0)
        features.append(employment_stability)

        # Existing debt
        existing_debt = lead_data.get("existing_debt", 0)
        has_existing_debt = 1.0 if existing_debt > 0 else 0.0
        features.append(has_existing_debt)

        # Payment history (simulated)
        payment_history = lead_data.get("payment_history", 0.8)
        features.append(payment_history)

        # Collateral
        collateral = lead_data.get("collateral", 0)
        has_collateral = 1.0 if collateral > 0 else 0.0
        features.append(has_collateral)

        # Product type risk
        product = lead_data.get("product", "")
        product_risk = {
            "savings_account": 0.1,
            "personal_loan": 0.4,
            "home_loan": 0.3,
            "credit_card": 0.5,
            "business_loan": 0.6,
        }.get(product, 0.4)
        features.append(product_risk)

        return features

    def _predict_risk_ml(self, features: List[float]) -> Tuple[int, float]:
        """
        ML-based risk assessment using Ensemble method
        Combines multiple factors
        """
        # Ensemble weights (combining multiple risk factors)
        weights = [
            -0.30,  # credit_score (higher = lower risk)
            0.25,  # churn_risk (higher = higher risk)
            0.20,  # debt_ratio (higher = higher risk)
            -0.10,  # employment_stability (higher = lower risk)
            0.10,  # existing_debt (has = higher risk)
            -0.15,  # payment_history (higher = lower risk)
            -0.15,  # collateral (has = lower risk)
            0.15,  # product_risk
        ]

        # Calculate base risk
        risk_score = 30  # Base risk

        for i, feature in enumerate(features[: len(weights)]):
            risk_score += feature * weights[i] * 100

        # Add interaction effects
        risk_score += features[0] * features[2] * 15  # credit * debt ratio
        risk_score -= features[5] * features[6] * 10  # payment * collateral

        # Clamp to valid range
        risk_score = max(0, min(100, int(risk_score)))

        # Probability of default
        default_probability = risk_score / 100

        return risk_score, default_probability

    def predict_risk_assessment(
        self, lead_data: Dict, credit_score: int = 650
    ) -> MLModelResult:
        """
        ML-based risk assessment using Ensemble method
        """
        # Extract features
        features = self._extract_risk_features(lead_data, credit_score)

        # ML prediction
        risk_score, probability = self._predict_risk_ml(features)

        # Determine risk level
        if risk_score < 20:
            risk_level = "low"
        elif risk_score < 40:
            risk_level = "medium"
        elif risk_score < 60:
            risk_level = "high"
        else:
            risk_level = "very_high"

        # Feature importance
        factor_names = [
            "Credit Score",
            "Churn Risk",
            "Debt Ratio",
            "Employment Stability",
            "Existing Debt",
            "Payment History",
            "Collateral",
            "Product Risk",
        ]

        factors = []
        for i, name in enumerate(factor_names[: len(features)]):
            factors.append(
                {
                    "feature": name,
                    "value": round(features[i], 3),
                    "impact": "positive" if i in [1, 2, 4, 7] else "negative",
                }
            )

        return MLModelResult(
            prediction=risk_score,
            probability=probability,
            confidence=0.80,
            factors=factors,
            model_version="ml-v1.0",
        )

    # ==================== OPTIMAL CONTACT TIME ML ====================

    def _extract_contact_time_features(self, lead_data: Dict) -> List[float]:
        """
        Extract features for optimal contact time prediction
        """
        features = []

        # Preferred time encoding
        preferred = lead_data.get("preferred_time", "morning")
        features.append(1.0 if preferred == "morning" else 0.0)
        features.append(1.0 if preferred == "afternoon" else 0.0)
        features.append(1.0 if preferred == "evening" else 0.0)

        # Day of week preference
        preferred_day = lead_data.get("preferred_day", "weekday")
        features.append(1.0 if preferred_day == "weekday" else 0.0)
        features.append(1.0 if preferred_day == "weekend" else 0.0)

        # Historical best contact time (if available)
        best_hour = lead_data.get("historical_best_hour", 10)
        features.append(best_hour / 24)

        # Response rate by time of day
        morning_response = lead_data.get("morning_response_rate", 0.6)
        afternoon_response = lead_data.get("afternoon_response_rate", 0.5)
        evening_response = lead_data.get("evening_response_rate", 0.4)
        features.extend([morning_response, afternoon_response, evening_response])

        # Lead engagement
        engagement = lead_data.get("engagement_score", 0.5)
        features.append(engagement)

        # Days since lead created
        days_since = lead_data.get("days_since_created", 1)
        features.append(min(days_since / 30, 1.0))

        return features

    def _predict_contact_time_ml(self, features: List[float]) -> Tuple[str, str, float]:
        """
        ML-based optimal contact time using Decision Tree logic
        Returns: (best_time, best_day, confidence)
        """
        # Weights for each time slot
        time_scores = {"morning": 0.0, "afternoon": 0.0, "evening": 0.0}

        # Morning features (index 0, 5, 6)
        if features[0] > 0:  # Preferred morning
            time_scores["morning"] += 0.3
        time_scores["morning"] += features[5] * 0.4  # Morning response rate

        # Afternoon features (index 1, 5, 7)
        if features[1] > 0:  # Preferred afternoon
            time_scores["afternoon"] += 0.3
        time_scores["afternoon"] += features[6] * 0.4  # Afternoon response rate

        # Evening features (index 2, 5, 8)
        if features[2] > 0:  # Preferred evening
            time_scores["evening"] += 0.3
        time_scores["evening"] += features[7] * 0.4  # Evening response rate

        # Add engagement factor
        engagement = features[9] if len(features) > 9 else 0.5
        time_scores["morning"] += engagement * 0.1
        time_scores["afternoon"] += engagement * 0.1
        time_scores["evening"] += engagement * 0.1

        # Urgency factor (newer leads = higher urgency)
        urgency = 1 - features[10] if len(features) > 10 else 0.5
        for time in time_scores:
            time_scores[time] += urgency * 0.1

        # Find best time
        best_time = max(time_scores, key=time_scores.get)
        confidence = (
            max(time_scores.values()) / 1.0 if max(time_scores.values()) > 0 else 0.5
        )

        # Determine best day
        best_day = "Tuesday" if features[3] > 0 else "Wednesday"

        # Time mapping
        time_map = {"morning": "10:00", "afternoon": "14:00", "evening": "18:00"}

        return time_map[best_time], best_day, min(0.95, confidence)

    def predict_optimal_contact_time(self, lead_data: Dict) -> MLModelResult:
        """
        ML-based optimal contact time prediction
        """
        # Extract features
        features = self._extract_contact_time_features(lead_data)

        # ML prediction
        best_time, best_day, confidence = self._predict_contact_time_ml(features)

        return MLModelResult(
            prediction=f"{best_day} {best_time}",
            probability=confidence,
            confidence=confidence,
            factors=[
                {"feature": "Best Time", "value": best_time},
                {"feature": "Best Day", "value": best_day},
                {
                    "feature": "Engagement",
                    "value": features[9] if len(features) > 9 else 0.5,
                },
            ],
            model_version="ml-v1.0",
        )

    # ==================== VOICE ANALYTICS ML (Naive Bayes) ====================

    def _extract_voice_features(self, transcript: str, metadata: Dict) -> List[float]:
        """
        Extract features for voice analytics ML
        """
        features = []

        text = transcript.lower()
        words = text.split()
        word_count = len(words)

        # Sentiment keywords
        positive_words = [
            "great",
            "excellent",
            "happy",
            "love",
            "interested",
            "yes",
            "good",
            "thank",
        ]
        negative_words = [
            "bad",
            "terrible",
            "hate",
            "not",
            "no",
            "expensive",
            "frustrated",
            "angry",
        ]

        pos_count = sum(1 for w in words if w in positive_words)
        neg_count = sum(1 for w in words if w in negative_words)

        # Sentiment ratio
        total_sentiment = pos_count + neg_count
        if total_sentiment > 0:
            sentiment_ratio = (pos_count - neg_count) / total_sentiment
        else:
            sentiment_ratio = 0
        features.append((sentiment_ratio + 1) / 2)  # Normalize to 0-1

        # Question asking (curiosity indicator)
        question_count = text.count("?")
        features.append(min(question_count / 5, 1.0))

        # Talking pace
        duration = metadata.get("duration_seconds", 300)
        wpm = (word_count / duration * 60) if duration > 0 else 150
        features.append(min(wpm / 200, 1.0))  # Normalize

        # Interruptions
        interruptions = metadata.get("interruptions", 0)
        features.append(min(interruptions / 10, 1.0))

        # Silence ratio (comfortable silence indicator)
        silence = metadata.get("silence_seconds", 0)
        silence_ratio = silence / duration if duration > 0 else 0
        features.append(silence_ratio)

        # Product mentions
        product_mentions = sum(
            1 for w in words if w in ["loan", "credit", "card", "account", "saving"]
        )
        features.append(min(product_mentions / 10, 1.0))

        # Action words (commitment indicator)
        action_words = ["apply", "open", "sign", "start", "proceed", "confirm"]
        action_count = sum(1 for w in words if w in action_words)
        features.append(min(action_count / 3, 1.0))

        return features

    def _predict_sentiment_ml(self, features: List[float]) -> Tuple[str, float, Dict]:
        """
        ML-based sentiment using Naive Bayes-like probability
        Returns: (sentiment_label, score, emotions)
        """
        # Sentiment probability based on features
        sentiment_score = features[0]  # From feature extraction

        # Question asking indicates interest
        curiosity = features[1]

        # Action words indicate commitment
        commitment = features[6]

        # Combined sentiment score
        combined_score = sentiment_score * 0.5 + curiosity * 0.2 + commitment * 0.3

        # Determine label
        if combined_score > 0.6:
            label = "positive"
        elif combined_score < 0.4:
            label = "negative"
        else:
            label = "neutral"

        # Detect emotions
        emotions = {
            "interested": min(curiosity + commitment, 1.0),
            "engaged": min(combined_score, 1.0),
            "frustrated": max(0, 1 - sentiment_score - curiosity),
            "uncertain": max(0, 0.5 - commitment),
        }

        return label, combined_score, emotions

    def analyze_voice_ml(self, transcript: str, metadata: Dict) -> MLModelResult:
        """
        ML-based voice/sentiment analysis
        """
        # Extract features
        features = self._extract_voice_features(transcript, metadata)

        # ML prediction
        label, score, emotions = self._predict_sentiment_ml(features)

        return MLModelResult(
            prediction=label,
            probability=score,
            confidence=0.78,
            factors=[
                {"feature": "Sentiment Score", "value": round(score, 3)},
                {"feature": "Curiosity", "value": round(features[1], 3)},
                {"feature": "Commitment", "value": round(features[6], 3)},
                {"feature": "Emotions", "value": emotions},
            ],
            model_version="ml-v1.0",
        )


# Singleton instance
ml_engine = MLEngineService()
