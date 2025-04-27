from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

class ActivitypubConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webapp.activitypub"

    label = "activitypub"
    verbose_name = _("activitypub")
    path = "@"
        # Activity signals


    def ready(self):
        from . import registry
        from .models import Actor, Note
        from .signals import createActor, signalHandler, action
        from webapp.models import Profile
        from django.conf import settings

        post_save.connect(createActor, sender=Profile)

        settings = settings._wrapped.__dict__
        settings.setdefault("BLOCKED_SERVERS", [])
        settings.setdefault("FETCH_RELATIONS", False)

        try:
            registry.register(Actor)
            registry.register(Note)
        except ImportError as e:
            logger.error(f"Model for 'Actor' not installed {e}")
        except Exception as e:
            logger.error(f"Cannot register `Actor` for Activities. {e}")

        action.connect(signalHandler, dispatch_uid="activitypub")
        logger.info("WebApp ready.")
