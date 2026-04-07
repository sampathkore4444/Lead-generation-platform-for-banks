"""
Core Banking Integration Service
Handles integration with STBank's core banking system
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging

import httpx

from ..config.settings import settings


logger = logging.getLogger(__name__)


class CoreBankingService:
    """Service for core banking integrations"""

    def __init__(self):
        self.base_url = settings.core_banking_url
        self.api_key = settings.core_banking_api_key

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def check_customer_exists(self, lao_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if customer exists in core banking system.
        Returns customer data if exists, None otherwise.
        """
        if not self.base_url:
            logger.warning("Core banking URL not configured")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/customers/{lao_id}",
                    headers=self._get_headers(),
                    timeout=10.0,
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    logger.error(f"Core banking API error: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            logger.error("Core banking API timeout")
            return None
        except Exception as e:
            logger.error(f"Core banking API error: {e}")
            return None

    async def get_customer_accounts(self, customer_id: str) -> Optional[list]:
        """
        Get customer's existing accounts.
        """
        if not self.base_url:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/customers/{customer_id}/accounts",
                    headers=self._get_headers(),
                    timeout=10.0,
                )

                if response.status_code == 200:
                    return response.json()
                return None

        except Exception as e:
            logger.error(f"Core banking API error: {e}")
            return None

    async def get_customer_kyc_status(
        self, customer_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get customer's KYC status.
        """
        if not self.base_url:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/customers/{customer_id}/kyc",
                    headers=self._get_headers(),
                    timeout=10.0,
                )

                if response.status_code == 200:
                    return response.json()
                return None

        except Exception as e:
            logger.error(f"Core banking API error: {e}")
            return None

    async def check_existing_loan(self, lao_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if customer has existing loans.
        """
        if not self.base_url:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/customers/{lao_id}/loans",
                    headers=self._get_headers(),
                    timeout=10.0,
                )

                if response.status_code == 200:
                    return response.json()
                return None

        except Exception as e:
            logger.error(f"Core banking API error: {e}")
            return None

    async def create_lead_reference(
        self, lead_id: int, customer_id: str, product: str, amount: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a lead/reference in core banking system.
        """
        if not self.base_url:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/leads",
                    headers=self._get_headers(),
                    json={
                        "external_id": lead_id,
                        "customer_id": customer_id,
                        "product": product,
                        "amount": amount,
                        "source": "LEADGEN",
                        "created_at": datetime.utcnow().isoformat(),
                    },
                    timeout=10.0,
                )

                if response.status_code in [200, 201]:
                    return response.json()
                return None

        except Exception as e:
            logger.error(f"Core banking API error: {e}")
            return None

    async def update_lead_status(
        self, reference_id: str, status: str, notes: Optional[str] = None
    ) -> bool:
        """
        Update lead status in core banking system.
        """
        if not self.base_url:
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/leads/{reference_id}",
                    headers=self._get_headers(),
                    json={
                        "status": status,
                        "notes": notes,
                        "updated_at": datetime.utcnow().isoformat(),
                    },
                    timeout=10.0,
                )

                return response.status_code in [200, 204]

        except Exception as e:
            logger.error(f"Core banking API error: {e}")
            return False


class CoreBankingService:
    """Mock service for development/testing"""

    async def check_customer_exists(self, lao_id: str) -> Optional[Dict[str, Any]]:
        """Mock - always returns None (no customer found)"""
        # Return mock data for testing
        # In production, replace with actual API call
        logger.info(f"Mock: Checking customer {lao_id}")
        return None

    async def get_customer_accounts(self, customer_id: str) -> Optional[list]:
        """Mock - returns empty list"""
        return []

    async def get_customer_kyc_status(
        self, customer_id: str
    ) -> Optional[Dict[str, Any]]:
        """Mock - returns not verified"""
        return {"status": "not_verified", "level": 0}

    async def check_existing_loan(self, lao_id: str) -> Optional[Dict[str, Any]]:
        """Mock - returns no loans"""
        return {"has_loans": False, "total_outstanding": 0}

    async def create_lead_reference(
        self, lead_id: int, customer_id: str, product: str, amount: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Mock - returns success"""
        return {"reference_id": f"REF-{lead_id}", "status": "pending"}

    async def update_lead_status(
        self, reference_id: str, status: str, notes: Optional[str] = None
    ) -> bool:
        """Mock - returns success"""
        return True


# Create singleton instance
core_banking = CoreBankingService()
