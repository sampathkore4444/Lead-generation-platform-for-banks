"""
Integration Services
Voice, WhatsApp/Line, Sentiment Analysis, Fraud Detection
"""

from typing import Optional, Dict, Any
import logging
import re

import httpx

from ..config.settings import settings


logger = logging.getLogger(__name__)


class VoiceService:
    """WebRTC Voice/Call integration"""

    def __init__(self):
        # In production, integrate with:
        # - Twilio
        # - WebRTC gateway
        # - Lao Telecom
        pass

    async def initiate_call(self, phone: str, lead_id: int) -> Dict[str, Any]:
        """Initiate outbound call to lead"""
        # Validate phone
        clean_phone = self._clean_phone(phone)

        return {
            "call_id": f"CALL-{lead_id}",
            "status": "initiated",
            "phone": clean_phone,
            "lead_id": lead_id,
            "duration_seconds": 0,
            "recording_url": None,
        }

    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Get call status"""
        return {
            "call_id": call_id,
            "status": "completed",
            "duration_seconds": 180,
            "recording_url": f"/recordings/{call_id}.wav",
        }

    def _clean_phone(self, phone: str) -> str:
        """Clean phone number"""
        # Remove all non-digits
        digits = re.sub(r"\D", "", phone)

        # Add country code if missing
        if digits.startswith("20"):
            return f"+856{digits}"
        elif not digits.startswith("856"):
            return f"+85620{digits}"
        return digits


class WhatsAppService:
    """WhatsApp/Line Integration for Laos market"""

    def __init__(self):
        self.whatsapp_enabled = getattr(settings, "whatsapp_enabled", False)
        self.line_enabled = getattr(settings, "line_enabled", False)

    async def send_whatsapp(self, phone: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp message"""
        if not self.whatsapp_enabled:
            return {"error": "WhatsApp not enabled"}

        # In production, integrate with WhatsApp Business API
        logger.info(f"WhatsApp to {phone}: {message}")

        return {
            "message_id": f"WA-{phone}-{id(message)}",
            "status": "sent",
            "channel": "whatsapp",
        }

    async def send_template(
        self, phone: str, template: str, params: Dict[str, str]
    ) -> Dict[str, Any]:
        """Send WhatsApp template message"""
        templates = {
            "lead_assignment": "Hi {name}! A new lead has been assigned to you. Product: {product}, Phone: {phone}",
            "lead_status": "Lead #{lead_id} status updated to: {status}",
            "reminder": "Reminder: Please contact lead #{lead_id} within 1 hour. SLA: {time_remaining} minutes remaining.",
        }

        message = templates.get(template, "").format(**params)
        return await self.send_whatsapp(phone, message)

    async def send_line(self, user_id: str, message: str) -> Dict[str, Any]:
        """Send LINE message"""
        if not self.line_enabled:
            return {"error": "LINE not enabled"}

        # In production, integrate with LINE Messaging API
        logger.info(f"LINE to {user_id}: {message}")

        return {
            "message_id": f"LINE-{user_id}-{id(message)}",
            "status": "sent",
            "channel": "line",
        }

    async def notify_new_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Notify sales rep of new lead via WhatsApp"""
        phone = lead_data.get("assigned_rep_phone")
        if not phone:
            return {"error": "No phone for rep"}

        template_params = {
            "name": lead_data.get("assigned_rep_name", "Rep"),
            "product": lead_data.get("product", ""),
            "phone": lead_data.get("phone", ""),
        }

        return await self.send_template(phone, "lead_assignment", template_params)


class SentimentService:
    """Sentiment Analysis for call recordings/chats"""

    def __init__(self):
        self.ollama_url = settings.ollama_url
        self.ollama_model = settings.ollama_model
        self.enabled = settings.ai_analytics_enabled

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        if not self.enabled:
            return self._rule_based_sentiment(text)

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.ollama_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Analyze sentiment. Reply ONLY with: positive, neutral, or negative",
                        },
                        {"role": "user", "content": text[:500]},
                    ],
                    "stream": False,
                }

                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    sentiment = (
                        data.get("message", {}).get("content", "").lower().strip()
                    )

                    score = (
                        1.0
                        if "positive" in sentiment
                        else -1.0 if "negative" in sentiment else 0.0
                    )

                    return {
                        "sentiment": sentiment,
                        "score": score,
                        "confidence": 0.85,
                    }
        except:
            pass

        return self._rule_based_sentiment(text)

    def _rule_based_sentiment(self, text: str) -> Dict[str, Any]:
        """Rule-based sentiment (fallback)"""
        positive_words = [
            "thank",
            "great",
            "good",
            "happy",
            "yes",
            "interested",
            "approve",
        ]
        negative_words = [
            "no",
            "not",
            "bad",
            "angry",
            "lost",
            "problem",
            "issue",
            "complaint",
        ]

        text_lower = text.lower()

        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        if pos_count > neg_count:
            return {"sentiment": "positive", "score": 0.7, "confidence": 0.5}
        elif neg_count > pos_count:
            return {"sentiment": "negative", "score": -0.7, "confidence": 0.5}

        return {"sentiment": "neutral", "score": 0.0, "confidence": 0.5}

    async def analyze_call_recording(self, recording_url: str) -> Dict[str, Any]:
        """Analyze call recording for sentiment"""
        # In production, integrate with speech-to-text + sentiment
        return {
            "sentiment": "positive",
            "score": 0.8,
            "key_topics": ["product inquiry", "interested"],
            "summary": "Customer interested in product",
        }


class FraudDetectionService:
    """Fraud Detection for lead submissions"""

    def __init__(self):
        self.enabled = True

    async def check_fraud(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check lead for fraud indicators"""
        risk_score = 0
        flags = []

        phone = lead_data.get("phone", "")

        # Check 1: Suspicious phone patterns
        if phone:
            # All same digits
            if len(set(phone)) == 1:
                risk_score += 30
                flags.append("suspicious_phone_pattern")

            # Invalid format
            if not phone.startswith("20") or len(phone) != 11:
                risk_score += 20
                flags.append("invalid_phone_format")

        # Check 2: Suspicious amount
        amount = lead_data.get("amount", 0)
        if amount:
            if amount > 500000000:  # Over limit
                risk_score += 40
                flags.append("exceeds_max_amount")
            if amount < 1000000:  # Under minimum
                risk_score += 10
                flags.append("below_minimum_amount")

        # Check 3: Duplicate submission pattern
        if lead_data.get("resubmit_count", 0) > 3:
            risk_score += 20
            flags.append("high_resubmit_count")

        # Determine risk level
        if risk_score >= 50:
            risk_level = "high"
            recommendation = "manual_review"
        elif risk_score >= 25:
            risk_level = "medium"
            recommendation = "verify"
        else:
            risk_level = "low"
            recommendation = "approve"

        return {
            "risk_score": min(risk_score, 100),
            "risk_level": risk_level,
            "flags": flags,
            "recommendation": recommendation,
            "requires_review": risk_level != "low",
        }

    async def check_ip_fraud(self, ip_address: str) -> Dict[str, Any]:
        """Check IP for fraud indicators"""
        # In production, integrate with:
        # - IP fraud databases
        # - Geo-location analysis
        # - VPN proxy detection

        return {
            "is_vpn": False,
            "is_proxy": False,
            "country": "LA",
            "risk_score": 0,
        }


# Singleton instances
voice_service = VoiceService()
whatsapp_service = WhatsAppService()
sentiment_service = SentimentService()
fraud_detection = FraudDetectionService()
