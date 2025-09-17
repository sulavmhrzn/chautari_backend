import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task
def send_welcome_email(first_name, email):
    message = "We are excited to have you on the platform"
    send_mail(
        subject=f"Welcome to Chautari, {first_name}",
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL"),
        recipient_list=[email],
    )
    logger.info(f"Sent welcome email to {email}")


@shared_task
def send_email_verification():
    # TODO: Implement email verification logic (e.g., send verification email to user)
    pass
