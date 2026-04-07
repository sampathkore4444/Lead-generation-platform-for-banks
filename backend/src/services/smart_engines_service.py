"""
Smart Engines Service
Advanced AI/ML engines for STBank Lead Generation Platform

Includes:
1. Credit Scoring Engine
2. Product Recommendation Engine
3. Speech/Voice Analytics
4. Churn Prediction
5. Optimal Contact Time Engine
6. Conversation Intelligence
7. Risk Assessment Engine
8. Auto-Scheduler
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import random
import json
import httpx


class CreditRating(str, Enum):
    """Credit rating categories"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    VERY_POOR = "very_poor"


class RiskLevel(str, Enum):
    """Risk level categories"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ProductRecommendation(str, Enum):
    """Recommended products"""

    SAVINGS_ACCOUNT = "savings_account"
    PERSONAL_LOAN = "personal_loan"
    HOME_LOAN = "home_loan"
    CREDIT_CARD = "credit_card"
    BUSINESS_LOAN = "business_loan"
    FIXED_DEPOSIT = "fixed_deposit"


@dataclass
class CreditScoreResult:
    """Credit scoring result"""

    score: int  # 300-850
    rating: CreditRating
    factors: List[str]
    recommendations: List[str]
    max_loan_amount: int
    suggested_rate: float


@dataclass
class ProductRecommendationResult:
    """Product recommendation result"""

    products: List[Dict[str, Any]]
    primary_recommendation: str
    confidence: float
    reasoning: List[str]


@dataclass
class ChurnPredictionResult:
    """Churn prediction result"""

    churn_probability: float  # 0-1
    risk_level: str
    factors: List[str]
    retention_suggestions: List[str]


@dataclass
class ContactTimeResult:
    """Optimal contact time result"""

    best_time: str
    best_day: str
    confidence: float
    reasoning: str


@dataclass
class VoiceAnalyticsResult:
    """Voice/speech analytics result"""

    sentiment_score: float  # -1 to 1
    sentiment_label: str
    keywords: List[str]
    topics: List[str]
    talk_ratio: Dict[str, float]
    interruption_count: int
    speaking_pace: float  # words per minute
    emotions: List[Dict[str, float]]
    compliance_mentions: List[str]


@dataclass
class ConversationIntelligenceResult:
    """Conversation intelligence result"""

    call_summary: str
    action_items: List[str]
    next_steps: List[str]
    lead_interest_level: str
    qualification_status: str
    key_objections: List[str]
    closing_signals: List[str]
    recommended_next_action: str


@dataclass
class RiskAssessmentResult:
    """Comprehensive risk assessment"""

    overall_risk_score: int  # 0-100
    risk_level: RiskLevel
    risk_factors: List[Dict[str, Any]]
    mitigation_suggestions: List[str]
    fraud_indicators: List[str]
    credit_considerations: List[str]


@dataclass
class ScheduleRecommendation:
    """Auto-scheduler result"""

    scheduled_time: datetime
    duration_minutes: int
    channel: str  # call, whatsapp, email
    priority: str
    reason: str


class SmartEnginesService:
    """
    Central service for all smart engines
    Uses Ollama for AI-powered analysis with rule-based fallback
    """

    def __init__(self):
        from backend.src.config.settings import settings

        self.settings = settings
        self.ollama_enabled = settings.OLLAMA_ENABLED
        self.ollama_url = settings.OLLAMA_URL
        self.ollama_model = settings.OLLAMA_MODEL

    async def _call_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """
        Call Ollama API for AI-powered analysis
        Returns the response text
        """
        import httpx

        if not self.ollama_enabled:
            return ""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                }
                if system_prompt:
                    payload["system"] = system_prompt

                response = await client.post(
                    f"{self.ollama_url}/api/generate", json=payload
                )

                if response.status_code == 200:
                    return response.json().get("response", "")
        except Exception as e:
            print(f"Ollama error: {e}")

        return ""

    # ==================== CREDIT SCORING ENGINE ====================

    async def calculate_credit_score(self, lead_data: Dict) -> CreditScoreResult:
        """
        Calculate credit score for a lead
        Uses multiple factors to determine creditworthiness
        """
        if self.ollama_enabled:
            return await self._ai_credit_score(lead_data)
        else:
            return self._rule_based_credit_score(lead_data)

    def _rule_based_credit_score(self, lead_data: Dict) -> CreditScoreResult:
        """Rule-based credit scoring (fallback)"""

        score = 500  # Base score
        factors = []
        recommendations = []

        # Amount factor
        amount = lead_data.get("amount", 0)
        if amount > 0:
            if amount < 50000000:  # < 50M LAK
                score += 50
                factors.append("Conservative loan amount")
            elif amount > 300000000:  # > 300M LAK
                score -= 30
                factors.append("High loan amount requires thorough review")

        # Product type factor
        product = lead_data.get("product", "")
        if product == "savings_account":
            score += 40
            factors.append("Savings account holders show financial discipline")
        elif product == "home_loan":
            score += 20
            factors.append("Home loans have collateral")

        # Phone format validation
        phone = lead_data.get("phone", "")
        if phone.startswith("20") and len(phone) == 11:
            score += 20
            factors.append("Valid phone format indicates local resident")

        # Generate rating
        if score >= 750:
            rating = CreditRating.EXCELLENT
            max_loan = 500000000
            rate = 8.0
        elif score >= 700:
            rating = CreditRating.GOOD
            max_loan = 300000000
            rate = 10.0
        elif score >= 650:
            rating = CreditRating.FAIR
            max_loan = 150000000
            rate = 12.0
        elif score >= 600:
            rating = CreditRating.POOR
            max_loan = 50000000
            rate = 15.0
        else:
            rating = CreditRating.VERY_POOR
            max_loan = 10000000
            rate = 18.0

        # Recommendations
        if rating in [CreditRating.EXCELLENT, CreditRating.GOOD]:
            recommendations.append("Approve with standard terms")
            recommendations.append("Consider offering premium credit card")
        elif rating == CreditRating.FAIR:
            recommendations.append("Request additional documentation")
            recommendations.append("Consider co-signer")
        else:
            recommendations.append("Require collateral or guarantee")
            recommendations.append("Start with small loan amount")

        return CreditScoreResult(
            score=score,
            rating=rating,
            factors=factors,
            recommendations=recommendations,
            max_loan_amount=max_loan,
            suggested_rate=rate,
        )

    async def _ai_credit_score(self, lead_data: Dict) -> CreditScoreResult:
        """AI-powered credit scoring using Ollama"""
        # In production, this would use Ollama for analysis
        # For now, use rule-based as base
        return self._rule_based_credit_score(lead_data)

    # ==================== PRODUCT RECOMMENDATION ENGINE ====================

    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        """
        Calculate Jaccard similarity between two sets
        Jaccard = |A ∩ B| / |A ∪ B|
        Returns value between 0 and 1
        """
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0

    def _get_lead_attributes(self, lead_data: Dict) -> set:
        """
        Extract lead attributes as a set for Jaccard comparison
        """
        attributes = set()

        # Product interest
        product = lead_data.get("product", "").lower()
        if product:
            attributes.add(product)
            # Add related attributes
            if "loan" in product:
                attributes.add("needs_credit")
                attributes.add("has_financial_goal")
            if "saving" in product:
                attributes.add("wants_to_save")
            if "credit" in product:
                attributes.add("needs_credit")
            if "home" in product or "house" in product:
                attributes.add("property_related")
                attributes.add("long_term")
            if "business" in product:
                attributes.add("business_owner")
                attributes.add("commercial")

        # Amount-based attributes
        amount = lead_data.get("amount", 0)
        if amount > 0:
            attributes.add("has_specified_amount")
            if amount < 20000000:
                attributes.add("small_amount")
            elif amount < 100000000:
                attributes.add("medium_amount")
            else:
                attributes.add("large_amount")

        # Phone-based attributes (Lao market)
        phone = lead_data.get("phone", "")
        if phone.startswith("20"):
            attributes.add("individual_phone")
        if phone.startswith("21") or phone.startswith("30"):
            attributes.add("business_phone")

        # Status attributes
        status = lead_data.get("status", "")
        if status == "new":
            attributes.add("new_customer")
        elif status in ["contacted", "qualified"]:
            attributes.add("warm_lead")

        return attributes

    def _get_product_attributes(self, product_type: str) -> set:
        """
        Get product attribute set for Jaccard comparison
        """
        # Product feature sets
        product_features = {
            "savings_account": {
                "wants_to_save",
                "needs_banking",
                "individual_phone",
                "small_amount",
                "medium_amount",
                "new_customer",
            },
            "personal_loan": {
                "needs_credit",
                "has_financial_goal",
                "individual_phone",
                "small_amount",
                "medium_amount",
                "personal_use",
            },
            "home_loan": {
                "needs_credit",
                "has_financial_goal",
                "property_related",
                "long_term",
                "large_amount",
                "medium_amount",
            },
            "credit_card": {
                "needs_credit",
                "individual_phone",
                "small_amount",
                "has_specified_amount",
            },
            "business_loan": {
                "needs_credit",
                "business_owner",
                "commercial",
                "has_financial_goal",
                "business_phone",
                "large_amount",
            },
            "fixed_deposit": {
                "wants_to_save",
                "medium_amount",
                "large_amount",
                "long_term",
                "has_specified_amount",
            },
        }

        return product_features.get(product_type, set())

    async def recommend_products(self, lead_data: Dict) -> ProductRecommendationResult:
        """
        Recommend best products for a lead using Jaccard similarity
        """
        products = []

        # Get lead attributes for Jaccard
        lead_attributes = self._get_lead_attributes(lead_data)

        # Analyze lead profile
        product = lead_data.get("product", "")
        amount = lead_data.get("amount", 0)

        # Product list with their attribute sets
        product_list = [
            ("savings_account", "Savings Account", "Foundational banking product"),
            ("personal_loan", "Personal Loan", "Quick personal financing"),
            ("home_loan", "Home Loan", "Property financing"),
            ("credit_card", "Credit Card", "Credit for everyday use"),
            ("business_loan", "Business Loan", "Business financing"),
            ("fixed_deposit", "Fixed Deposit", "Secure savings"),
        ]

        # Calculate Jaccard similarity for each product
        for prod_key, prod_name, prod_desc in product_list:
            product_attrs = self._get_product_attributes(prod_key)
            jaccard_score = self._jaccard_similarity(lead_attributes, product_attrs)

            # Convert to 0-100 score (weight: 70% Jaccard + 30% rules)
            base_score = jaccard_score * 100

            # Add rule-based boost for explicit product interest
            if product == prod_key:
                base_score = min(95, base_score + 25)

            # Add amount-based adjustments
            if prod_key == "personal_loan" and 0 < amount < 100000000:
                base_score = min(95, base_score + 10)
            elif prod_key == "home_loan" and 50000000 <= amount <= 500000000:
                base_score = min(95, base_score + 10)
            elif prod_key == "credit_card" and amount < 20000000:
                base_score = min(95, base_score + 10)

            products.append(
                {
                    "product": prod_key,
                    "name": prod_name,
                    "jaccard_score": round(jaccard_score, 3),
                    "score": int(base_score),
                    "reason": prod_desc,
                    "matching_attributes": list(
                        lead_attributes.intersection(product_attrs)
                    ),
                }
            )

        # Sort by score
        products.sort(key=lambda x: x["score"], reverse=True)

        # Calculate confidence based on best Jaccard score
        best_jaccard = products[0]["jaccard_score"] if products else 0
        confidence = min(0.95, 0.5 + best_jaccard * 0.5)

        # Build reasoning with matching attributes
        matching_attrs = products[0].get("matching_attributes", []) if products else []
        reasoning = [
            f"Jaccard similarity: {best_jaccard:.1%}",
            f"Matched attributes: {', '.join(matching_attrs) if matching_attrs else 'none'}",
            f"Customer interest: {product or 'exploring options'}",
        ]

        return ProductRecommendationResult(
            products=products[:3],
            primary_recommendation=(
                products[0]["product"] if products else "savings_account"
            ),
            confidence=round(confidence, 2),
            reasoning=reasoning,
        )

    # ==================== CHURN PREDICTION ENGINE ====================

    async def predict_churn(
        self, lead_data: Dict, interaction_history: List[Dict]
    ) -> ChurnPredictionResult:
        """
        Predict likelihood of lead dropping off
        """
        probability = 0.2  # Base probability
        factors = []
        suggestions = []

        # Time since last contact
        last_contact = lead_data.get("last_contact")
        if last_contact:
            days_since = (datetime.now() - last_contact).days
            if days_since > 7:
                probability += 0.3
                factors.append(f"No contact for {days_since} days")
        else:
            probability += 0.2
            factors.append("Never contacted")

        # Number of interactions
        interaction_count = len(interaction_history)
        if interaction_count == 0:
            probability += 0.2
            factors.append("No interaction history")

        # Response rate
        response_rate = lead_data.get("response_rate", 1.0)
        if response_rate < 0.5:
            probability += 0.2
            factors.append("Low response rate")

        # Status
        status = lead_data.get("status", "")
        if status == "lost":
            probability = 0.95
        elif status == "contacted":
            probability -= 0.1

        # Determine risk level
        if probability < 0.3:
            risk_level = "low"
            suggestions.append("Continue standard follow-up")
        elif probability < 0.5:
            risk_level = "medium"
            suggestions.append("Schedule follow-up within 2 days")
        elif probability < 0.7:
            risk_level = "high"
            suggestions.append("Immediate personal contact recommended")
        else:
            risk_level = "very_high"
            suggestions.append("Escalate to manager - high churn risk")

        return ChurnPredictionResult(
            churn_probability=probability,
            risk_level=risk_level,
            factors=factors,
            retention_suggestions=suggestions,
        )

    # ==================== OPTIMAL CONTACT TIME ENGINE ====================

    async def predict_optimal_contact_time(self, lead_data: Dict) -> ContactTimeResult:
        """
        Predict best time to contact lead for highest conversion
        """
        # Analyze from lead data
        preferred_time = lead_data.get("preferred_time", "")

        # Default times based on Lao market
        time_mapping = {
            "morning": ("09:00", "Monday", 0.8),
            "afternoon": ("14:00", "Tuesday", 0.75),
            "evening": ("18:00", "Wednesday", 0.7),
        }

        if preferred_time.lower() in time_mapping:
            time, day, conf = time_mapping[preferred_time.lower()]
        else:
            # Default to morning mid-week
            time, day, conf = "10:00", "Wednesday", 0.7

        return ContactTimeResult(
            best_time=time,
            best_day=day,
            confidence=conf,
            reasoning=f"Based on Lao market patterns and stated preference: {preferred_time}",
        )

    # ==================== SPEECH/VOICE ANALYTICS ====================

    async def analyze_voice_call(
        self, call_transcript: str, metadata: Dict
    ) -> VoiceAnalyticsResult:
        """
        Analyze voice call recording/transcript
        """
        # Basic sentiment analysis
        positive_words = [
            "interested",
            "yes",
            "good",
            "great",
            "thank",
            "please",
            "okay",
        ]
        negative_words = ["no", "not", "expensive", "later", "busy", "wrong"]
        neutral_words = ["okay", "yes", "understand"]

        words = call_transcript.lower().split()

        pos_count = sum(1 for w in words if w in positive_words)
        neg_count = sum(1 for w in words if w in negative_words)

        if pos_count + neg_count > 0:
            sentiment = (pos_count - neg_count) / (pos_count + neg_count)
        else:
            sentiment = 0.0

        # Sentiment label
        if sentiment > 0.3:
            label = "positive"
        elif sentiment < -0.3:
            label = "negative"
        else:
            label = "neutral"

        # Extract keywords
        keywords = [w for w in words if w in positive_words + negative_words][:10]

        # Topics
        topics = []
        if any(w in words for w in ["loan", "credit", "amount", "rate"]):
            topics.append("loan_products")
        if any(w in words for w in ["account", "saving", "deposit"]):
            topics.append("accounts")
        if any(w in words for w in ["card", "credit"]):
            topics.append("cards")
        if any(w in words for w in ["house", "home", "property"]):
            topics.append("property")

        # Talk ratio (simulated)
        talk_ratio = {"agent": 0.4, "lead": 0.6}

        # Compliance mentions
        compliance_keywords = ["consent", "agree", "privacy", "data", "terms"]
        compliance_mentions = [w for w in words if w in compliance_keywords]

        return VoiceAnalyticsResult(
            sentiment_score=sentiment,
            sentiment_label=label,
            keywords=keywords,
            topics=topics,
            talk_ratio=talk_ratio,
            interruption_count=metadata.get("interruptions", 0),
            speaking_pace=metadata.get("wpm", 150),
            emotions=self._detect_emotions(call_transcript),
            compliance_mentions=compliance_mentions,
        )

    def _detect_emotions(self, text: str) -> List[Dict[str, float]]:
        """Detect emotions from text"""
        emotions = {
            "happy": 0.0,
            "interested": 0.0,
            "frustrated": 0.0,
            "uncertain": 0.0,
        }

        text_lower = text.lower()

        # Simple keyword-based emotion detection
        if any(w in text_lower for w in ["great", "excellent", "happy", "love"]):
            emotions["happy"] = 0.7
        if any(w in text_lower for w in ["interested", "tell me more", "yes"]):
            emotions["interested"] = 0.8
        if any(w in text_lower for w in ["frustrated", "annoyed", "terrible"]):
            emotions["frustrated"] = 0.6
        if any(w in text_lower for w in ["maybe", "not sure", "perhaps"]):
            emotions["uncertain"] = 0.5

        return [{"emotion": k, "score": v} for k, v in emotions.items() if v > 0]

    # ==================== CONVERSATION INTELLIGENCE ====================

    async def analyze_conversation(
        self, transcript: str, agent_notes: str
    ) -> ConversationIntelligenceResult:
        """
        Comprehensive conversation analysis using Ollama AI
        """
        # Try AI analysis first
        if self.ollama_enabled:
            try:
                ai_result = await self._analyze_conversation_ai(transcript, agent_notes)
                if ai_result:
                    return ai_result
            except Exception as e:
                print(f"Ollama conversation analysis error: {e}")

        # Fallback to rule-based
        return self._rule_based_conversation(transcript, agent_notes)

    async def _analyze_conversation_ai(
        self, transcript: str, agent_notes: str
    ) -> Optional[ConversationIntelligenceResult]:
        """AI-powered conversation analysis using Ollama"""
        import json

        prompt = f"""Analyze this sales call transcript.

TRANSCRIPT: {transcript}

AGENT NOTES: {agent_notes}

Respond with JSON:
{{"summary": "brief", "interest_level": "high/medium/low", "qualification": "qualified/pending/not_qualified", "objections": ["price"], "closing_signals": [], "action_items": [], "next_steps": []}}"""

        system_prompt = "You are a sales analyst. Respond ONLY with valid JSON."
        response = await self._call_ollama(prompt, system_prompt)

        if response:
            try:
                # Extract JSON from response
                data = json.loads(response)
                return ConversationIntelligenceResult(
                    call_summary=data.get("summary", ""),
                    action_items=data.get("action_items", []),
                    next_steps=data.get("next_steps", []),
                    lead_interest_level=data.get("interest_level", "medium"),
                    qualification_status=data.get("qualification", "pending"),
                    key_objections=data.get("objections", []),
                    closing_signals=data.get("closing_signals", []),
                    recommended_next_action=(
                        data.get("action_items", ["follow_up"])[0]
                        if data.get("action_items")
                        else "follow_up"
                    ),
                )
            except:
                pass

        return None

    def _rule_based_conversation(
        self, transcript: str, agent_notes: str
    ) -> ConversationIntelligenceResult:
        """Rule-based conversation analysis (fallback)"""
        text = (transcript + " " + agent_notes).lower()

        interest_indicators = [
            "interested",
            "yes please",
            "tell me more",
            "sounds good",
            "great",
        ]
        disinterest_indicators = ["not interested", "maybe later", "busy", "call back"]

        interest_count = sum(1 for w in interest_indicators if w in text)
        disinterest_count = sum(1 for w in disinterest_indicators if w in text)

        interest_level = (
            "high"
            if interest_count > disinterest_count
            else ("medium" if interest_count == disinterest_count else "low")
        )

        if any(w in text for w in ["ready", "apply", "documents", "account"]):
            qualification = "qualified"
        elif any(w in text for w in ["consider", "thinking", "maybe"]):
            qualification = "pending"
        else:
            qualification = "not_qualified"

        objections = []
        if any(k in text for k in ["expensive", "rate", "cost"]):
            objections.append("price")
        if any(k in text for k in ["busy", "later", "time"]):
            objections.append("time")

        closing_signals = []
        if any(w in text for w in ["next step", "how to apply"]):
            closing_signals.append("asking_next_steps")

        summary = f"Customer shows {interest_level} interest level."

        return ConversationIntelligenceResult(
            call_summary=summary,
            action_items=[
                (
                    "Follow up within 24 hours"
                    if interest_level == "high"
                    else "Schedule next call"
                )
            ],
            next_steps=(
                ["Send product details", "Schedule appointment"]
                if qualification == "qualified"
                else ["Send educational content"]
            ),
            lead_interest_level=interest_level,
            qualification_status=qualification,
            key_objections=objections,
            closing_signals=closing_signals,
            recommended_next_action=(
                "send_follow_up_email"
                if interest_level == "high"
                else "schedule_discovery_call"
            ),
        )

    # ==================== RISK ASSESSMENT ENGINE ====================

    async def assess_risk(
        self, lead_data: Dict, credit_score: int, fraud_indicators: List[str]
    ) -> RiskAssessmentResult:
        """
        Comprehensive risk assessment combining multiple factors
        """
        risk_score = 0
        risk_factors = []
        mitigations = []

        # Credit score factor
        if credit_score < 600:
            risk_score += 40
            risk_factors.append(
                {
                    "category": "credit",
                    "severity": "high",
                    "description": "Low credit score",
                }
            )
            mitigations.append("Require collateral or co-signer")
        elif credit_score < 700:
            risk_score += 20
            risk_factors.append(
                {
                    "category": "credit",
                    "severity": "medium",
                    "description": "Fair credit score",
                }
            )
            mitigations.append("Review additional documentation")

        # Fraud indicators
        fraud_count = len(fraud_indicators)
        if fraud_count > 0:
            risk_score += 50 * fraud_count
            for indicator in fraud_indicators:
                risk_factors.append(
                    {
                        "category": "fraud",
                        "severity": "critical",
                        "description": indicator,
                    }
                )
            mitigations.append("Flag for manual review")

        # Amount risk
        amount = lead_data.get("amount", 0)
        if amount > 300000000:
            risk_score += 15
            risk_factors.append(
                {
                    "category": "amount",
                    "severity": "medium",
                    "description": "High loan amount",
                }
            )
            mitigations.append("Require additional verification")

        # Phone validation
        phone = lead_data.get("phone", "")
        if not phone.startswith("20"):
            risk_score += 10
            risk_factors.append(
                {
                    "category": "contact",
                    "severity": "low",
                    "description": "Non-standard phone format",
                }
            )

        # Determine overall risk level
        if risk_score < 20:
            level = RiskLevel.LOW
        elif risk_score < 40:
            level = RiskLevel.MEDIUM
        elif risk_score < 60:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.VERY_HIGH

        return RiskAssessmentResult(
            overall_risk_score=min(risk_score, 100),
            risk_level=level,
            risk_factors=risk_factors,
            mitigation_suggestions=mitigations,
            fraud_indicators=fraud_indicators,
            credit_considerations=(
                ["Review credit history", "Check payment capacity"]
                if credit_score < 700
                else []
            ),
        )

    # ==================== AUTO-SCHEDULER ====================

    async def generate_schedule_recommendation(
        self, lead_data: Dict, agent_availability: List[Dict], priority: str = "normal"
    ) -> ScheduleRecommendation:
        """
        Generate automatic schedule recommendation for follow-up
        """
        # Get optimal time
        contact_result = await self.predict_optimal_contact_time(lead_data)

        # Determine channel
        phone = lead_data.get("phone", "")
        product = lead_data.get("product", "")

        if phone.startswith("20"):
            channel = "call"  # Direct line
        else:
            channel = "whatsapp"

        # High-value products get phone calls
        if product in ["home_loan", "business_loan"]:
            channel = "call"

        # Determine duration
        if product in ["home_loan", "business_loan"]:
            duration = 30
        elif product == "personal_loan":
            duration = 20
        else:
            duration = 15

        # Calculate scheduled time
        day_map = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
        }

        from datetime import datetime, timedelta

        current = datetime.now()
        target_day = day_map.get(contact_result.best_day, 2)

        days_ahead = target_day - current.weekday()
        if days_ahead <= 0:
            days_ahead += 7

        scheduled = current + timedelta(days=days_ahead)

        # Parse time
        hour, minute = map(int, contact_result.best_time.split(":"))
        scheduled = scheduled.replace(hour=hour, minute=minute, second=0)

        return ScheduleRecommendation(
            scheduled_time=scheduled,
            duration_minutes=duration,
            channel=channel,
            priority=priority,
            reason=f"Based on {contact_result.best_day} {contact_result.best_time} preference and {channel} channel",
        )


# Singleton instance
smart_engines = SmartEnginesService()
