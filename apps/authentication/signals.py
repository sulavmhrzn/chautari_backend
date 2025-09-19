from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.authentication.models import Profile, User
from apps.authentication.tasks import send_welcome_and_verification_email


@receiver(post_save, sender=User)
def create_user_profile(instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        send_welcome_and_verification_email.delay(
            first_name=instance.first_name, email=instance.email
        )
