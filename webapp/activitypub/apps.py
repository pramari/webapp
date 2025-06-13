from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)

class ActivitypubConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webapp.activitypub"

    label = "activitypub"
    verbose_name = _("activitypub")
    path = "@"

    def ready(self):
        from webapp.activitypub import registry
        from webapp.activitypub.models import Actor, Note, Like
        from webapp.activitypub.signals import createActor, signalHandler, action
        from webapp.models import Profile
        from django.conf import settings

        logger.error("Successfully working with ActivityPub")

        post_save.connect(createActor, sender=Profile)

        settings = settings._wrapped.__dict__
        settings.setdefault("BLOCKED_SERVERS", [])
        settings.setdefault("FETCH_RELATIONS", False)

        try:
            registry.register(Actor)
        except ImportError as e:
            logger.error(f"Model for 'Actor' not installed {e}")
        except ImproperlyConfigured as e:
            logger.error(f"Cannot register `Actor` for Activities. {e}")
        except ValueError as e:
            logger.error(f"Fucking fix this error: {e}")

        try:
            registry.register(Like)
            registry.register(Note)
        except ImportError as e:
            logger.error(f"Model for 'Like' not installed {e}")
        except ImproperlyConfigured as e:
            logger.error(f"Cannot register `Like` for Activities. {e}")
        except ValueError as e:
            logger.error(f"Fucking fix this error: {e}")

        action.connect(signalHandler, dispatch_uid="activitypub")
        logger.info("WebApp ready.")
