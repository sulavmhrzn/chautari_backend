from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.authentication.models import Profile, User


@receiver(post_save, sender=User)
def create_user_profile(instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)
