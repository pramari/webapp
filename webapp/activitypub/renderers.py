"""renderers.py

    .. seealso:: https://www.w3.org/ns/activitystreams

    .. seealso::
    https://www.django-rest-framework.org/api-guide/renderers/#custom-renderers

    Returns:
        _type_: _description_
"""

import logging
from rest_framework import renderers

logger = logging.getLogger(__name__)


class JrdRenderer(renderers.JSONRenderer):
    """
    JrdRenderer

    Accept: 'application/json' for WebFinger Requests.
    """

    media_type = "application/jrd+json"
    format = "jrd"


class JsonLDRenderer(renderers.JSONRenderer):
    """
    JsonLDRenderer

    Args:
        renderers (JsonLDRenderer): Renders JSON-LD data

    Returns:
        JsonLD: Added Context to JSON-LD data
    """

    media_type = "application/ld+json"
    format = "ld"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        logger.debug("ActivityRenderer.render: media_type:" + str(accepted_media_type))

        assert isinstance(data, dict), "JsonLDRenderer.render expects a dict"

        data["@context"] = ["https://www.w3.org/ns/activitystreams"]
        # if data.get("publicKey"):
        #     data["@context"].append("https://w3id.org/security/v1")

        try:
            from rdflib import Graph
        except ImportError as e:
            logger.error("JsonLDRenderer.render: rdflib not installed: " + str(e))
            raise ImportError("rdflib is required for JsonLDRenderer")
        except Exception as e:
            logger.error("JsonLDRenderer.render: Unexpected error: " + str(e))
            raise Exception("Unexpected error during rdflib import")

        return super().render(
            dict(sorted(data.items())), accepted_media_type, renderer_context
        )


class ActivityRenderer(renderers.JSONRenderer):
    """
    ActivitypubRenderer
    """

    media_type = "application/activity+json"  # ; profile="https://www.w3.org/ns/activitystreams"'
    format = "activity"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        logger.debug("ActivityRenderer.render: media_type:" + str(accepted_media_type))

        data["@context"] = ["https://www.w3.org/ns/activitystreams"]
        if data.get("publicKey"):
            data["@context"].append("https://w3id.org/security/v1")

        return super().render(data, accepted_media_type, renderer_context)
