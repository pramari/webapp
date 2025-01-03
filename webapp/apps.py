import logging

from allauth.account.signals import (
    email_added,
    email_confirmed,
    email_removed,
    user_logged_in,
)
from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class WebAppConfig(AppConfig):
    """
    Configuration for the fedapp app.
    """

    name = "webapp"
    label = "webapp"
    verbose_name = _("webapp")
    path = "webapp"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # pylint: disable=C0415,C0103
        from django.db.models.signals import post_save

        from webapp import registry
        from webapp.models import Actor, Like, Note  # , Profile
        from webapp.signals import (
            action,
            createUserProfile,
            emailConfirmed,
            checkEmailVerified,
            signalHandler,
            signalLogger,
        )

        email_added.connect(signalLogger)  # , sender=EmailAddress)
        email_removed.connect(signalLogger)  # , sender=EmailAddress)

        email_confirmed.connect(emailConfirmed)

        user_logged_in.connect(checkEmailVerified)

        from django.conf import settings

        settings = settings._wrapped.__dict__
        settings.setdefault("BLOCKED_SERVERS", [])
        settings.setdefault("FETCH_RELATIONS", False)

        # Activity signals

        User = get_user_model()

        post_save.connect(createUserProfile, sender=User)

        try:
            registry.register(Actor)
            registry.register(Note)
            registry.register(Like)
        except ImportError as e:
            logger.error(f"Model for 'Actor' not installed {e}")
        except Exception as e:
            logger.error(f"Cannot register `Actor` for Activities. {e}")

        action.connect(signalHandler, dispatch_uid="activitypub")

        logger.info("WebApp ready.")
