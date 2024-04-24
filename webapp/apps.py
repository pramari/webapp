from django.apps import apps, AppConfig

from django.utils.timezone import now

from django.utils.translation import gettext_lazy as _


import logging

logger = logging.getLogger(__name__)


def register_signals():
    """
    Register signals for the webapp app.
    """
    from django.dispatch import Signal

    action = Signal()
    logger.error(f"In register_signals: action signal created: {action}")

    def handler(verb, **kwargs):
        """
        Handler function to create Action instance upon action signal call.
        """
        from django.contrib.contenttypes.models import ContentType
        from webapp.registry import check

        logger.error("Enter handler")

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
            timestamp=kwargs.pop("timestamp", now()),
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

    result = action.connect(handler)  # , dispatch_uid="webapp.models")
    logger.error(f"Connected action signal: {result}")


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
            from .models import Note, Profile

            registry.register(Note)
            logger.error("Successfully registered 'Note'")
            registry.register(Profile)
            logger.error("Successfully registered 'Profile'")
        except ImportError as e:
            logger.error(f"Model for 'Note' not installed {e}")
        except Exception as e:
            logger.error(f"Cannot register `Notes` for Activities. {e}")

        register_signals()
        logger.info("WebApp ready.")
