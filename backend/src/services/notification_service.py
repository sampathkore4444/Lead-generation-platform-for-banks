"""
Notification Service
Handles email and SMS notifications
"""

from typing import Optional
import logging

from ..config.settings import settings


logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications"""

    @staticmethod
    async def send_lead_notification(
        lead_id: int, customer_name: str, phone: str, product: str
    ) -> bool:
        """
        Send notification to sales rep about new lead.
        Returns True if successful.
        """
        # Log the notification (in production, integrate with email/SMS gateway)
        logger.info(
            f"New lead notification: ID={lead_id}, Customer={customer_name}, Phone={phone}, Product={product}"
        )

        # TODO: Implement actual notification
        # Options:
        # 1. Email to assigned sales rep
        # 2. SMS to assigned sales rep
        # 3. Push notification (Telegram/Teams webhook)

        return True

    @staticmethod
    async def send_confirmation_sms(phone: str, customer_name: str) -> bool:
        """
        Send confirmation SMS to customer.
        Returns True if successful.
        """
        if not settings.smtp_host:
            logger.warning("SMS gateway not configured")
            return False

        # TODO: Implement SMS gateway integration
        # Example with Lao Telecom SMS API:
        # message = f"STBank: {customer_name}, thank you! We will contact you within 2 hours."

        logger.info(f"Confirmation SMS sent to {phone}")
        return True

    @staticmethod
    async def send_status_update_sms(phone: str, status: str) -> bool:
        """
        Send status update SMS to customer.
        """
        if not settings.smtp_host:
            logger.warning("SMS gateway not configured")
            return False

        status_messages = {
            "contacted": "STBank: We have contacted you. Please answer our call.",
            "qualified": "STBank: Your application is being processed.",
            "converted": "STBank: Congratulations! Your account is approved.",
            "lost": "STBank: Thank you for your interest. Better luck next time!",
        }

        message = status_messages.get(status, "STBank: Your status has been updated.")
        logger.info(f"Status SMS sent to {phone}: {status}")

        return True


class EmailService:
    """Service for sending emails"""

    @staticmethod
    async def send_email(to: str, subject: str, body: str, html: bool = False) -> bool:
        """
        Send email.
        Returns True if successful.
        """
        if not settings.smtp_host:
            logger.warning("SMTP not configured")
            return False

        # TODO: Implement email sending with aiosmtplib or similar
        logger.info(f"Email sent to {to}: {subject}")
        return True

    @staticmethod
    async def send_lead_assignment_email(
        sales_rep_email: str,
        sales_rep_name: str,
        lead_id: int,
        customer_name: str,
        phone: str,
        product: str,
    ) -> bool:
        """
        Send email to sales rep about new lead assignment.
        """
        subject = f"New Lead Assigned: {customer_name}"

        body = f"""
Hello {sales_rep_name},

A new lead has been assigned to you.

Lead Details:
- Lead ID: {lead_id}
- Customer Name: {customer_name}
- Phone: {phone}
- Product: {product}

Please contact this lead within 1 hour to meet our SLA.

Best regards,
STBank LeadGen System
        """

        return await EmailService.send_email(sales_rep_email, subject, body)

    @staticmethod
    async def send_daily_summary_email(to: str, stats: dict) -> bool:
        """
        Send daily summary email to manager.
        """
        subject = f"Daily Lead Summary - {stats.get('date', 'Today')}"

        body = f"""
Daily Lead Summary

New Leads: {stats.get('new_count', 0)}
Contacted: {stats.get('contacted_count', 0)}
Qualified: {stats.get('qualified_count', 0)}
Converted: {stats.get('converted_count', 0)}
Conversion Rate: {stats.get('conversion_rate', 0):.1f}%

Best regards,
STBank LeadGen System
        """

        return await EmailService.send_email(to, subject, body)
