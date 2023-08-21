from django.contrib.auth import get_user_model
# from allauth.account.models import EmailAddress # unused? since 2023-08-07
import logging

from django.contrib.auth.signals import user_logged_in  # type: ignore
from django.db.models.signals import post_save          # type: ignore
from django.dispatch import receiver                    # type: ignore

logger = logging.getLogger(__name__)

User = get_user_model()


def signal_logger(request, **kwargs):
    logger.error(request)
    logger.error(kwargs)


@receiver(user_logged_in, sender=User)
def userLogin(sender, request, user, signal, *args, **kwargs):
    """
    Signal to process UserLogin
    """
    pass


def create_user_profile(sender, instance, created, **kwargs):
    """
    create a new profile instance for every user created.

    leverage `Django Signals` for this purpose.
    """
    if created:  # not user.profile:
        from .models import Profile
        Profile.objects.create(user=instance)


def make_activitypub_handle_on_profile(sender, instance, **kwargs):
    instance.ap_id = "https://pramari.de" + instance.get_absolute_url
