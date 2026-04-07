"""
MFA and CAPTCHA API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..middleware.auth import get_current_user
from ..models.user import User
from ..services.mfa_service import MFAService, CaptchaService

router = APIRouter(tags=["MFA"])


@router.post("/setup")
async def setup_mfa(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Setup MFA for the current user
    Returns secret and QR code for authenticator app
    """
    secret, qr_code = await MFAService.setup_mfa(db, current_user.id)

    return {
        "secret": secret,
        "qr_code": f"data:image/png;base64,{qr_code}",
        "message": "Scan QR code with your authenticator app, then verify with a code",
    }


@router.post("/enable")
async def enable_mfa(
    code: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Enable MFA after verifying a code from authenticator app
    """
    success = await MFAService.enable_mfa(db, current_user.id, code)

    if success:
        return {"message": "MFA enabled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid code. Please try again.")


@router.post("/verify")
async def verify_mfa(
    code: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Verify MFA code during login
    """
    # This is handled in the auth flow, but providing endpoint for testing
    if not current_user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA not enabled for this user")

    success = await MFAService.verify_mfa(db, current_user.id, code)

    return {"valid": success}


@router.post("/disable")
async def disable_mfa(
    password: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Disable MFA (requires password)
    """
    success = await MFAService.disable_mfa(db, current_user.id, password)

    if success:
        return {"message": "MFA disabled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid password")


@router.post("/regenerate-backup-codes")
async def regenerate_backup_codes(
    password: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Regenerate backup codes (requires password)
    """
    codes = await MFAService.regenerate_backup_codes(db, current_user.id, password)

    if codes:
        return {
            "backup_codes": codes,
            "message": "Save these backup codes in a secure place",
        }
    else:
        raise HTTPException(
            status_code=400, detail="Invalid password or MFA not enabled"
        )


# CAPTCHA endpoints
captcha_store = {}


@router.get("/captcha")
async def get_captcha():
    """
    Get a new CAPTCHA challenge
    """
    challenge = CaptchaService.generate_challenge()
    captcha_store[challenge["token"]] = challenge

    return {
        "token": challenge["token"],
        "question": challenge["question"],
        "type": challenge["type"],
    }


@router.post("/captcha/verify")
async def verify_captcha(request: Request):
    """
    Verify CAPTCHA answer
    """
    body = await request.json()
    token = body.get("token")
    answer = body.get("answer")
    challenge = captcha_store.get(token)

    if not challenge:
        raise HTTPException(status_code=400, detail="Invalid CAPTCHA token")

    # Check answer
    is_valid = CaptchaService.verify_answer(token, answer, challenge["answer_hash"])

    if is_valid:
        # Remove from store after successful verification
        captcha_store.pop(token, None)
        return {"valid": True}

    return {"valid": False}


@router.get("/captcha/honey")
async def get_honey_token():
    """
    Get honeypot token for bot detection
    """
    return {"token": CaptchaService.generate_honey_token()}
