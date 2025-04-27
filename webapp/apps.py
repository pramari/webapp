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

        from webapp.signals import (
            createUserProfile,
            emailConfirmed,
            checkEmailVerified,
            signalLogger,
        )

        email_added.connect(signalLogger)  # , sender=EmailAddress)
        email_removed.connect(signalLogger)  # , sender=EmailAddress)

        email_confirmed.connect(emailConfirmed)

        user_logged_in.connect(checkEmailVerified)

        # Activity signals

        User = get_user_model()

        post_save.connect(createUserProfile, sender=User)

        logger.info("WebApp ready.")
