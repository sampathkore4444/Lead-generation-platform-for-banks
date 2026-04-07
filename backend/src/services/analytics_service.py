"""
AI Analytics Service
Predictive insights and reporting with Ollama
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

import httpx

from ..config.settings import settings


logger = logging.getLogger(__name__)


class AnalyticsService:
    """AI-powered analytics and predictions"""

    def __init__(self):
        self.ollama_url = settings.ollama_url
        self.ollama_model = settings.ollama_model
        self.enabled = settings.ai_analytics_enabled

    async def generate_report(
        self, stats: Dict[str, Any], period: str = "daily"
    ) -> Optional[str]:
        """
        Generate AI-powered report summary.
        """
        if not self.enabled:
            return self._rule_based_report(stats, period)

        system_prompt = """You are a banking analytics expert.
Generate a brief, actionable report from the statistics.
Keep it under 4 bullet points. Start with key achievements."""

        prompt = f"""Generate a {period} report from this data:
- Total leads: {stats.get('total', 0)}
- New: {stats.get('new_count', 0)}
- Contacted: {stats.get('contacted_count', 0)}
- Qualified: {stats.get('qualified_count', 0)}
- Converted: {stats.get('converted_count', 0)}
- Conversion rate: {stats.get('conversion_rate', 0):.1f}%
- Avg contact time: {stats.get('avg_time_to_contact', 0):.0f} minutes
- SLA compliance: {stats.get('sla_compliance', 0):.1f}%"""

        return await self._call_ollama(
            prompt, system_prompt
        ) or self._rule_based_report(stats, period)

    async def _call_ollama(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Call Ollama API"""
        if not self.enabled:
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
                return None

        except Exception as e:
            logger.error(f"Analytics AI error: {e}")
            return None

    def _rule_based_report(self, stats: Dict[str, Any], period: str) -> str:
        """Rule-based report (fallback)"""
        lines = [
            f"📊 {period.title()} Report",
            f"• Total leads: {stats.get('total', 0)}",
            f"• Conversion rate: {stats.get('conversion_rate', 0):.1f}%",
            f"• SLA compliance: {stats.get('sla_compliance', 0):.1f}%",
        ]

        if stats.get("conversion_rate", 0) >= 20:
            lines.append("✅ Great conversion performance!")
        elif stats.get("conversion_rate", 0) >= 10:
            lines.append("📈 Good progress, keep it up!")
        else:
            lines.append("⚠️ Needs attention on conversion")

        return "\n".join(lines)

    async def predict_trend(
        self, historical_data: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Predict future trends based on historical data.
        """
        if not self.enabled or len(historical_data) < 7:
            return self._rule_based_prediction(historical_data)

        # Calculate basic trend
        recent = historical_data[-7:]
        total_leads = sum(d.get("total", 0) for d in recent)
        avg = total_leads / 7

        return {
            "predicted_leads_next_week": int(avg * 1.1),  # 10% growth
            "confidence": "medium",
            "trend": (
                "growing"
                if avg > (sum(d.get("total", 0) for d in historical_data[-14:-7]) / 7)
                else "stable"
            ),
            "recommendation": "Maintain current team allocation",
        }

    def _rule_based_prediction(
        self, historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Rule-based prediction (fallback)"""
        total = (
            sum(d.get("total", 0) for d in historical_data) if historical_data else 10
        )

        return {
            "predicted_leads_next_week": total,
            "confidence": "low",
            "trend": "stable",
            "recommendation": "Insufficient data for prediction",
        }

    async def analyze_rep_performance(
        self, rep_stats: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Analyze sales rep performance with AI insights.
        """
        if not self.enabled:
            return rep_stats

        # Add AI insights to each rep
        for rep in rep_stats:
            score = rep.get("score", 50)

            if score >= 80:
                rep["ai_insight"] = "🌟 Top performer - consider for mentoring"
            elif score >= 60:
                rep["ai_insight"] = "📈 Strong performer - keep current pace"
            elif score >= 40:
                rep["ai_insight"] = "📊 Meeting targets - room for growth"
            else:
                rep["ai_insight"] = "⚠️ Needs support - recommend coaching"

        return rep_stats

    async def suggest_pricing(
        self, product: str, amount: int, customer_profile: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest optimal pricing/terms for a lead.
        """
        # Simple rule-based pricing
        base_rate = 8.5  # Base rate for LAK loans

        if product == "home_loan":
            rate = base_rate - 1.5  # 7%
            tenure = 20
        elif product == "personal_loan":
            rate = base_rate + 2  # 10.5%
            tenure = 5
        else:
            rate = base_rate
            tenure = 3

        # Adjust for amount
        if amount >= 100000000:
            rate -= 0.5

        return {
            "suggested_rate": rate,
            "suggested_tenure_years": tenure,
            "max_eligible_amount": amount * 3,
            "reason": "Based on product type and amount",
        }


# Singleton instance
analytics_service = AnalyticsService()
