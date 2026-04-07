"""
AI Service with Ollama Integration
Lead scoring, predictions, and chatbot
"""

from typing import Optional, Dict, Any, List
import logging

import httpx

from ..config.settings import settings


logger = logging.getLogger(__name__)


class AIService:
    """AI Service for lead scoring and predictions"""

    def __init__(self):
        self.ollama_url = settings.ollama_url
        self.ollama_model = settings.ollama_model
        self.enabled = settings.ollama_enabled

    async def _call_ollama(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Call Ollama API"""
        if not self.enabled:
            logger.warning("Ollama is not enabled")
            return None

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.ollama_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                }

                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json=payload,
                    timeout=60.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("message", {}).get("content", "")
                else:
                    logger.error(f"Ollama API error: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            logger.error("Ollama API timeout")
            return None
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None

    async def score_lead(self, lead_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Score a lead for conversion probability.
        Returns score (0-100) and reason.
        """
        if not settings.ai_scoring_enabled:
            return self._rule_based_score(lead_data)

        system_prompt = """You are a banking lead scoring expert. 
Analyze the lead data and predict conversion probability.
Respond with ONLY a JSON object: {"score": 0-100, "reason": "brief reason", "recommendation": "high/medium/low"}"""

        prompt = f"""Analyze this lead:
- Name: {lead_data.get('full_name')}
- Product: {lead_data.get('product')}
- Amount: {lead_data.get('amount')}
- Phone format: {lead_data.get('phone', '')[0:3] if lead_data.get('phone') else 'unknown'}
- Preferred time: {lead_data.get('preferred_time')}

What is the conversion probability?"""

        result = await self._call_ollama(prompt, system_prompt)

        if result:
            try:
                # Try to parse JSON from response
                import json
                import re

                # Extract JSON from markdown if present
                json_match = re.search(r"\{.*\}", result, re.DOTALL)
                if json_match:
                    score_data = json.loads(json_match.group())
                    return score_data
            except:
                pass

        # Fallback to rule-based
        return self._rule_based_score(lead_data)

    def _rule_based_score(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based scoring (fallback)"""
        score = 50  # Base score
        reason = "Rule-based analysis"

        product = lead_data.get("product", "")
        amount = lead_data.get("amount", 0)

        # Product-based scoring
        if product == "savings_account":
            score += 15
            reason = "Savings account interest"
        elif product == "personal_loan":
            score += 10
            reason = "Personal loan inquiry"
        elif product == "home_loan":
            score += 20
            if amount and amount > 50000000:
                score += 10
                reason = "High-value home loan"
        elif product == "credit_card":
            score += 5

        # Amount-based scoring
        if amount and amount > 100000000:
            score += 10

        recommendation = "high" if score >= 70 else "medium" if score >= 50 else "low"

        return {
            "score": min(score, 100),
            "reason": reason,
            "recommendation": recommendation,
        }

    async def suggest_assignment(
        self, lead_data: Dict[str, Any], reps: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest best sales rep assignment based on lead characteristics.
        """
        if not reps:
            return None

        # Simple matching logic
        product = lead_data.get("product", "")

        # Match by product specialty
        for rep in reps:
            specialties = rep.get("specialties", [])
            if product in specialties:
                return rep

        # Fallback: return rep with lowest workload
        return min(reps, key=lambda r: r.get("active_leads", 0))

    async def generate_insight(self, lead_data: Dict[str, Any]) -> Optional[str]:
        """Generate AI insight about a lead"""
        if not settings.ai_scoring_enabled:
            return "Enable AI in settings for insights"

        system_prompt = """You are a bank customer insight expert.
Generate a brief insight about this potential customer.
Keep it under 2 sentences."""

        prompt = f"""Generate insight for this lead:
Full Name: {lead_data.get('full_name')}
Product Interest: {lead_data.get('product')}
Amount: {lead_data.get('amount', 'not specified')} LAK"""

        return await self._call_ollama(prompt, system_prompt)

    async def predict_conversion_time(self, lead_data: Dict[str, Any]) -> Optional[str]:
        """Predict when lead is likely to convert"""
        if not settings.ai_analytics_enabled:
            return "Within 1 week (estimate)"

        system_prompt = """You are a sales analytics expert.
Predict conversion timeline based on lead data.
Respond with ONLY: "Within X days" or "Within X weeks" """

        prompt = f"""Predict conversion timeframe:
Product: {lead_data.get('product')}
Amount: {lead_data.get('amount', 'not specified')} LAK
Lead quality score: {lead_data.get('score', 50)}"""

        return await self._call_ollama(prompt, system_prompt) or "Within 1 week"


class ChatbotService:
    """AI Chatbot for customer queries"""

    def __init__(self):
        self.ollama_url = settings.ollama_url
        self.ollama_model = settings.ollama_model
        self.enabled = settings.ai_chatbot_enabled

    async def chat(self, message: str, context: Dict[str, Any] = {}) -> str:
        """
        Handle customer chatbot message.
        """
        if not self.enabled:
            return self._rule_based_response(message)

        system_prompt = """You are STBank Laos customer service assistant.
Help customers with their banking inquiries.
Be helpful, concise, and friendly.
Respond in Lao (if needed) and English.
Do not ask for personal information."""

        # Add context if available
        if context.get("lead_name"):
            system_prompt += f"\nCurrent customer: {context['lead_name']}"

        result = await self._call_ollama(message, system_prompt)

        return result or self._rule_based_response(message)

    async def _call_ollama(self, message: str, system_prompt: str) -> Optional[str]:
        """Call Ollama for chatbot"""
        if not self.enabled:
            return None

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.ollama_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message},
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
                    return data.get("message", {}).get("content", "")
                return None

        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return None

    def _rule_based_response(self, message: str) -> str:
        """Rule-based fallback responses"""
        message_lower = message.lower()

        responses = {
            "hello": "Hello! Welcome to STBank Laos. How can I help you today?",
            "hi": "Hi there! How can I assist you?",
            "hours": "Our branches are open Mon-Fri 8:00-17:00 and Sat 8:00-12:00.",
            "location": "We have branches in Vientiane, Luang Prab, Pakse, and Savannakhet.",
            "loan": "We offer Personal Loans, Home Loans, and more. Would you like to apply?",
            "savings": "Our Savings Account offers competitive interest rates. Would you like to know more?",
            "credit": "Our Credit Cards come with great rewards. Apply today!",
            "contact": "Call 1629 or visit any STBank branch.",
            "default": "Thank you for your message. A representative will contact you within 2 hours.",
        }

        for key, response in responses.items():
            if key in message_lower:
                return response

        return responses["default"]

    async def get_product_info(self, product: str) -> str:
        """Get information about a product"""
        if not self.enabled:
            return self._rule_based_product_info(product)

        system_prompt = """You are STBank product information assistant.
Provide brief, accurate information about the product.
Keep response under 3 sentences."""

        prompt = f"Tell me about {product} at STBank Laos."

        return await self._call_ollama(
            prompt, system_prompt
        ) or self._rule_based_product_info(product)

    def _rule_based_product_info(self, product: str) -> str:
        """Rule-based product info"""
        info = {
            "savings": "Our Savings Account offers 4.5% annual interest with no minimum balance. Free ATM card included.",
            "personal": "Personal Loans up to 50M LAK with competitive rates. Approval in 24 hours.",
            "home": "Home Loans up to 500M LAK with 20-year tenure. Special rates for first-time buyers.",
            "credit": "STBank Credit Cards - Cashback rewards, free annual fee first year.",
        }
        return info.get(product.lower(), "Please visit stbank.la for more information.")


# Singleton instances
ai_service = AIService()
chatbot_service = ChatbotService()
