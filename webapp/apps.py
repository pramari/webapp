from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

import logging


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
        from webapp.signals import (
            action,
            signalHandler,
            signalLogger,
            createUserProfile,
        )
        from allauth.account.signals import email_added
        from allauth.account.signals import email_confirmed
        from allauth.account.signals import email_removed

        User = get_user_model()

        post_save.connect(createUserProfile, sender=User)

        email_added.connect(signalLogger)  # , sender=EmailAddress)
        email_confirmed.connect(signalLogger)  # , sender=EmailAddress)
        email_removed.connect(signalLogger)  # , sender=EmailAddress)

        # Activity signals

        try:
            from webapp import registry
            from .models import Note, Profile

            registry.register(Note)
            logger.error("Successfully registered 'Note'")
            registry.register(Profile)
            logger.error("Successfully registered 'Profile'")
        except ImportError as e:
            logger.error(f"Model for 'Note' not installed {e}")
        except Exception as e:
            logger.error(f"Cannot register `Notes` for Activities. {e}")

        action.connect(signalHandler, dispatch_uid="webapp.models")

        logger.info("WebApp ready.")
