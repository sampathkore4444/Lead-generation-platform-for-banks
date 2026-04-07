"""
On-Premise MFA Service using TOTP (Time-based One-Time Password)
Compatible with Google Authenticator, Microsoft Authenticator, etc.
"""

import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from ..models.user import User


class MFAService:
    """On-premise TOTP-based MFA service"""

    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(email: str, secret: str, issuer: str = "STBank Laos") -> str:
        """
        Generate QR code for authenticator app setup
        Returns base64 encoded PNG image
        """
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=email, issuer_name=issuer)

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode()

    @staticmethod
    def verify_code(secret: str, code: str, window: int = 1) -> bool:
        """
        Verify TOTP code with ±1 window for clock drift
        """
        totp = pyotp.TOTP(secret)

        # Check current code and ±1 window
        for offset in range(-window, window + 1):
            if totp.verify(code, valid_window=abs(offset)):
                return True
        return False

    @staticmethod
    def generate_backup_codes(count: int = 8) -> list[str]:
        """Generate backup codes for MFA recovery"""
        import secrets

        return [secrets.token_hex(4).upper() for _ in range(count)]

    @staticmethod
    async def setup_mfa(db: Session, user_id: int) -> Tuple[str, str]:
        """
        Setup MFA for a user
        Returns: (secret, qr_code_base64)
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Generate new secret
        secret = MFAService.generate_secret()

        # Generate QR code
        qr_code = MFAService.generate_qr_code(user.email, secret)

        # Store secret temporarily (not enabled until verified)
        user.mfa_secret = secret
        user.mfa_backup_codes = ",".join(MFAService.generate_backup_codes())
        db.commit()

        return secret, qr_code

    @staticmethod
    async def enable_mfa(db: Session, user_id: int, code: str) -> bool:
        """
        Enable MFA after user verifies a code
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.mfa_secret:
            return False

        if MFAService.verify_code(user.mfa_secret, code):
            user.mfa_enabled = True
            user.mfa_secret = user.mfa_secret  # Already stored
            user.mfa_enabled_at = datetime.utcnow()
            db.commit()
            return True

        return False

    @staticmethod
    async def verify_mfa(db: Session, user_id: int, code: str) -> bool:
        """
        Verify MFA code during login
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.mfa_enabled:
            return False

        # Check backup code first
        if user.mfa_backup_codes:
            codes = user.mfa_backup_codes.split(",")
            code_upper = code.upper()
            if code_upper in codes:
                # Remove used backup code
                codes.remove(code_upper)
                user.mfa_backup_codes = ",".join(codes)
                db.commit()
                return True

        # Check TOTP
        return MFAService.verify_code(user.mfa_secret, code)

    @staticmethod
    async def disable_mfa(db: Session, user_id: int, password: str) -> bool:
        """
        Disable MFA (requires password verification)
        """
        from backend.src.services.auth_service import AuthService

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        # Verify password
        if not AuthService.verify_password(password, user.password_hash):
            return False

        # Disable MFA
        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes = None
        user.mfa_enabled_at = None
        db.commit()

        return True

    @staticmethod
    async def regenerate_backup_codes(
        db: Session, user_id: int, password: str
    ) -> Optional[list[str]]:
        """
        Regenerate backup codes (requires password verification)
        """
        from backend.src.services.auth_service import AuthService

        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.mfa_enabled:
            return None

        # Verify password
        if not AuthService.verify_password(password, user.password_hash):
            return None

        # Generate new backup codes
        new_codes = MFAService.generate_backup_codes()
        user.mfa_backup_codes = ",".join(new_codes)
        db.commit()

        return new_codes


class CaptchaService:
    """
    On-premise CAPTCHA service (math-based + quiz)
    Alternative to Google reCAPTCHA for on-prem部署
    """

    CHALLENGES = [
        {"type": "math", "template": "{a} + {b} = ?", "operators": ["+"]},
        {
            "type": "math",
            "template": "{a} + {b} + {c} = ?",
            "operators": ["+"],
            " operands": 3,
        },
        {"type": "math", "template": "{a} × {b} = ?", "operators": ["*"]},
    ]

    @staticmethod
    def generate_challenge() -> dict:
        """Generate a new CAPTCHA challenge"""
        import random
        import string

        challenge = random.choice(CaptchaService.CHALLENGES)

        if challenge["type"] == "math":
            operands = challenge.get("operands", 2)
            operator = challenge["operators"][0]

            if operator == "+":
                if operands == 2:
                    a = random.randint(1, 20)
                    b = random.randint(1, 20)
                    answer = a + b
                    question = f"{a} + {b} = ?"
                else:
                    a = random.randint(1, 10)
                    b = random.randint(1, 10)
                    c = random.randint(1, 10)
                    answer = a + b + c
                    question = f"{a} + {b} + {c} = ?"
            else:  # multiplication
                a = random.randint(2, 10)
                b = random.randint(2, 10)
                answer = a * b
                question = f"{a} × {b} = ?"

            # Generate session token
            token = "".join(random.choices(string.ascii_letters + string.digits, k=32))

            return {
                "token": token,
                "question": question,
                "answer_hash": CaptchaService._hash_answer(answer, token),
                "type": "math",
            }

        return {}

    @staticmethod
    def _hash_answer(answer: int, token: str) -> str:
        """Hash the answer with token for verification"""
        import hashlib

        combined = f"{answer}:{token}:stbank_captcha_secret"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    @staticmethod
    def verify_answer(token: str, answer: str, answer_hash: str) -> bool:
        """Verify CAPTCHA answer"""
        import hashlib

        try:
            answer_int = int(answer)
            expected_hash = CaptchaService._hash_answer(answer_int, token)
            return expected_hash == answer_hash
        except (ValueError, TypeError):
            return False

    @staticmethod
    def generate_honey_token() -> str:
        """Generate honeypot token for bot detection"""
        import secrets

        return secrets.token_urlsafe(32)
