import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in  # type: ignore
from django.dispatch import receiver  # type: ignore
from django.dispatch import Signal

logger = logging.getLogger(__name__)

action = Signal()
"""Action signal."""

User = get_user_model()
"""User model."""


def signalLogger(request, **kwargs):
    """
    Generic signal logger.

    args:
        request: The request object.
        **kwargs: Additional keyword arguments.
    """
    logger.error(request)
    logger.error(kwargs)


@receiver(action)
def signalHandler(verb, **kwargs):
    """
    Handler function to create Action instance upon action signal call.

    This function is called whenever an action signal is called. It creates an
    instance of the Action model and saves it to the database.

    Args:
        verb (str): The action verb.
        **kwargs: Additional keyword arguments for the action.
    """
    from django.contrib.contenttypes.models import ContentType
    from django.apps import apps
    from django.utils import timezone
    from webapp.registry import check

    logger.error("Entering signal handler")

    kwargs.pop("signal", None)
    actor = kwargs.pop("sender")

    # We must store the untranslated string
    # If verb is an ugettext_lazyed string, fetch the original string
    if hasattr(verb, "_proxy____args"):
        verb = verb._proxy____args[0]

    action = apps.get_model("webapp", "action")(
        actor_content_type=ContentType.objects.get_for_model(actor),
        actor_object_id=actor.pk,
        verb=str(verb),
        public=bool(kwargs.pop("public", True)),
        description=kwargs.pop("description", None),
        timestamp=kwargs.pop("timestamp", timezone.now()),
    )

    for opt in ("target", "action_object"):
        obj = kwargs.pop(opt, None)
        if obj is not None:
            check(obj)
            setattr(action, "{opt}_object_id", obj.pk)
            setattr(
                action,
                f"{opt}_content_type",
                ContentType.objects.get_for_model(obj),
            )
    action.save(force_insert=True)
    logger.error("In action_handler")
    return action


@receiver(user_logged_in, sender=User)
def userLogin(sender, request, user, signal, *args, **kwargs):
    """
    Signal to process UserLogin
    """
    pass


def createUserProfile(sender, instance, created, **kwargs):
    """
    create a new profile instance for every user created.

    leverage `Django Signals` for this purpose.
    """
    if created:  # not user.profile:
        from .models import Profile

        Profile.objects.create(user=instance)


def make_activitypub_handle_on_profile(sender, instance, **kwargs):
    instance.ap_id = "https://pramari.de" + instance.get_absolute_url
