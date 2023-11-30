from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import logging
logger = logging.getLogger(__name__)


class WebAppConfig(AppConfig):
    name = 'webapp'
    label = 'webapp'
    verbose_name = _('webapp')
    path = "webapp"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # pylint: disable=C0415,C0103
        from django.contrib.auth import get_user_model
        from django.db.models.signals import pre_save, post_save
        from webapp.models import Profile
        from webapp.signals import (
            signal_logger,
            create_user_profile,
        )
        from allauth.account.signals import (
            email_added,
            email_confirmed,
            email_removed
            )

        User = get_user_model()

        post_save.connect(create_user_profile, sender=User)

        email_added.connect(signal_logger)  # , sender=EmailAddress)
        email_confirmed.connect(signal_logger)  # , sender=EmailAddress)
        email_removed.connect(signal_logger)  # , sender=EmailAddress)
        logger.info("WebApp ready.")
