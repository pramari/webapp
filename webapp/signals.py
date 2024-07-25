import logging

from django.contrib.auth import get_user_model
from django.dispatch import Signal
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.utils import timezone
from webapp.registry import check


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


def signalHandler(*args, **kwargs):
    """
    Handler function to create Action instance upon action signal call.

    This function is called whenever an action signal is called. It creates an
    instance of the Action model and saves it to the database.

    Reference:
        https://github.com/justquick/django-activity-stream/blob/main/actstream/actions.py

    Args:
        verb (str): The action verb.
        **kwargs: Additional keyword arguments for the action.

    Usage:
        from webapp.models import Actor, Note
        from webapp.signals import action
        a = Actor.objects.get(id="https://pramari.de/@andreas")
        n = Note.objects.all()[0]

        action.send(sender=a, actor=a, verb="created", action_object=n)

    """
    logger.debug("Entering signal handler")
    signal = kwargs.pop("signal", None)  # noqa: F841
    actor = kwargs.pop("sender")
    verb = kwargs.pop("verb")

    # We must store the untranslated string
    # If verb is an ugettext_lazyed string, fetch the original string
    if hasattr(verb, "_proxy____args"):
        verb = verb._proxy____args[0]

    actor_content_type = ContentType.objects.get_for_model(actor)
    actor_object_id = actor.pk

    activity = apps.get_model("webapp", "action")(
        actor_content_type=actor_content_type,
        actor_object_id=actor_object_id,
        activity_type=str(verb).lower(),
        public=bool(kwargs.pop("public", True)),
        description=kwargs.pop("description", None),
        timestamp=kwargs.pop("timestamp", timezone.now()),
    )

    # for opt in ("target", "action_object"):
    target = kwargs.pop("target", None)
    if target is not None:
        check(target)  # Check if the object is registered
        setattr(activity, "target_object_id", target.pk)
        setattr(
            activity,
            "target_content_type",
            ContentType.objects.get_for_model(target),
        )

    action_object = kwargs.pop("action_object", None)
    if action_object is not None:
        check(action_object)  # Check if the object is registered
        setattr(activity, "action_object_object_id", action_object.pk)
        setattr(
            activity,
            "action_object_content_type",
            ContentType.objects.get_for_model(action_object),
        )

    activity.save(force_insert=True)
    logger.debug("Succesfully exited signalHandler")
    return activity


"""
@receiver(user_logged_in, sender=User)
def userLogin(sender, request, user, signal, *args, **kwargs):
    pass
"""


def createUserProfile(sender, instance, created, **kwargs):
    """
    create a new profile instance for every user created.

    leverage `Django Signals` for this purpose.
    """
    if created:  # not user.profile:
        from .models import Profile, Actor

        # from django.contrib.sites.models import Site

        # base = f"https://{Site.objects.get_current().domain}"
        base = "https://pramari.de"
        profile = Profile.objects.create(user=instance, slug=instance.username)
        Actor.objects.create(
            profile=profile, type="Person", id=f"{base}/@{instance.username}"
        )
