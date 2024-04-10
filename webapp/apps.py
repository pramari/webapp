from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)


class WebAppConfig(AppConfig):
    name = "webapp"
    label = "webapp"
    verbose_name = _("webapp")
    path = "webapp"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # pylint: disable=C0415,C0103
        from django.contrib.auth import get_user_model
        from django.db.models.signals import post_save
        from webapp.signals import (
            signal_logger,
            create_user_profile,
        )
        from allauth.account.signals import email_added
        from allauth.account.signals import email_confirmed
        from allauth.account.signals import email_removed

        User = get_user_model()

        post_save.connect(create_user_profile, sender=User)

        email_added.connect(signal_logger)  # , sender=EmailAddress)
        email_confirmed.connect(signal_logger)  # , sender=EmailAddress)
        email_removed.connect(signal_logger)  # , sender=EmailAddress)

        # Activity signals

        try:
            from webapp import registry
        except ImportError as e:
            logger.error("webapp.registry not installed. %s", e)

        try:
            from pages.models import ActivityPubNote

            registry.register(ActivityPubNote)
        except ImportError as e:
            logger.error(f"Model for 'Note' not installed {e}")
        except Exception as e:
            logger.error("Cannot register `Notes` for Activities. %s", e)

        logger.info("WebApp ready.")
