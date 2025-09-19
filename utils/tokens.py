import secrets
import string
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.authentication.models import TOKEN_TYPES, VerificationToken


def _generate_secure_token(length=12):
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _generate_numeric_code(length=6):
    """Generate a random numeric code for email/SMS verification"""
    return "".join(secrets.choice(string.digits) for _ in range(length))


def create_verification_token(user, token_type, expires_in_minutes, use_numeric=False):
    """Create a verification token for a user"""
    token = _generate_numeric_code() if use_numeric else _generate_secure_token()
    expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)

    return VerificationToken.objects.create(
        user=user, token=token, token_type=token_type, expires_at=expires_at
    )


def create_email_verification_token(user, **kwargs):
    """Create an email verification token."""
    return create_verification_token(
        user=user,
        token_type=TOKEN_TYPES.EMAIL_VERIFICATION,
        expires_in_minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRES_IN_MINUTES,
        use_numeric=True,
        **kwargs,
    )


def create_password_reset_token(user, **kwargs):
    pass
