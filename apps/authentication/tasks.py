import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.authentication.models import VerificationToken
from apps.listings.models import User
from utils.tokens import create_email_verification_token

logger = logging.getLogger(__name__)


@shared_task
def send_welcome_and_verification_email(first_name, email):
    """
    Asynchronously send welcome email with verification token to new user.
    """

    # TODO: Use django template
    user = User.objects.get(email=email)
    verification_token = create_email_verification_token(user)
    message = f"""We are excited to have you on the platform.
    Your email verification token is {verification_token.token}.
    This token will expire in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRES_IN_MINUTES} minutes.
    """

    send_mail(
        subject=f"Welcome to Chautari, {first_name}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
    logger.info(f"Sent welcome email to {email}")


@shared_task
def delete_verification_tokens():
    tokens = VerificationToken.objects.filter(expires_at__lte=timezone.now())
    count, _ = tokens.delete()
    logger.info(f"deleted {count} expired verification tokens")


@shared_task
def send_verification_email(first_name, email, token):
    """
    Asynchronously send email with verification token to an unverified user.
    """

    # TODO: Use django template
    message = f"""We are excited to have you on the platform.
    Your email verification token is {token}.
    This token will expire in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRES_IN_MINUTES} minutes.
    """
    send_mail(
        subject=f"Welcome to Chautari, {first_name}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
    logger.info(f"Sent verification email to {email}")


@shared_task
def send_password_reset_email(first_name, email, token):
    message = f"""
    Hello, {first_name}. We received a password reset request for your account.
    If this wasn't you, you can ignore this message.
    Your password reset token is {token}.
    This token will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRES_IN_MINUTES} minutes."""
    send_mail(
        subject="Password Reset Request",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
    logger.info(f"Sent password reset email to {email}")
