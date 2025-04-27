"""renderers.py

    .. seealso:: https://www.w3.org/ns/activitystreams

    .. seealso::
    https://www.django-rest-framework.org/api-guide/renderers/#custom-renderers

    Returns:
        _type_: _description_
"""

import json
import logging

import contextlib
from rest_framework import renderers

from rest_framework.utils import encoders
from rest_framework.settings import api_settings
from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.compat import (
    INDENT_SEPARATORS,
    LONG_SEPARATORS,
    SHORT_SEPARATORS,
)
from rest_framework.exceptions import NotAcceptable

from django.utils.http import parse_header_parameters

logger = logging.getLogger(__name__)


class WebappContentNegotiation(DefaultContentNegotiation):
    """
    WebappContentNegotiation

    """

    def select_parser(self, request, parsers):
        logger.debug("WebappContentNegotiation.select_parser")
        logger.debug("request: " + str(request))
        logger.debug("parsers: " + str(parsers))
        return super().select_parser(request, parsers)

    def select_renderer(self, request, renderers, format_suffix):
        try:
            selected_renderer = super().select_renderer(
                request, renderers, format_suffix
            )
        except NotAcceptable:
            errormessage = f"""WebappContentNegotiation.select_renderer\n
                request: (accept) \t{str(request.headers.get("accept"))}\n
                renderers: \t{str(renderers)}\n
                media_types: \t{str([renderer.media_type for renderer in renderers])}\n
                format_suffix: \t{str(format_suffix)}\n
                """
            logger.debug(errormessage)
            raise NotAcceptable(errormessage)
        return selected_renderer


def zero_as_none(value):
    return None if value == 0 else value


class WebAppBaseRenderer(renderers.BaseRenderer):
    """
    WebAppBaseRenderer

    """

    encoder_class = encoders.JSONEncoder  # inherited from JSONRenderer
    ensure_ascii = not api_settings.UNICODE_JSON  # inherited from JSONRenderer
    compact = api_settings.COMPACT_JSON  # inherited from JSONRenderer
    strict = api_settings.STRICT_JSON  # same as JSONRenderer
    charset = None  # because it's a binary format

    def get_indent(self, accepted_media_type, renderer_context):
        if accepted_media_type:
            # If the media type looks like 'application/json; indent=4',
            # then pretty print the result.
            # Note that we coerce `indent=0` into `indent=None`.
            base_media_type, params = parse_header_parameters(accepted_media_type)
            with contextlib.suppress(KeyError, ValueError, TypeError):
                return zero_as_none(max(min(int(params["indent"]), 8), 0))
        # If 'indent' is provided in the context, then pretty print the result.
        # E.g. If we're being called by the BrowsableAPIRenderer.
        return renderer_context.get("indent", None)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        logger.debug("JsonLDRenderer.render: media_type:" + str(accepted_media_type))
        if data is None:
            return b""
        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS

        ret = json.dumps(
            data,
            cls=self.encoder_class,
            ensure_ascii=self.ensure_ascii,
            allow_nan=not self.strict,
            indent=indent,
            separators=separators,
        )

        # We always fully escape \u2028 and \u2029 to ensure we output JSON
        # that is a strict javascript subset.
        # See: https://gist.github.com/damncabbage/623b879af56f850a6ddc
        ret = ret.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        return ret.encode()


class JsonLDRenderer(WebAppBaseRenderer):
    """
    JsonLDRenderer

    Args:
        renderers (JsonLDRenderer): Renders JSON-LD data

    Returns:
        JsonLD: Added Context to JSON-LD data
    """

    accepted_media_type = (
        'application/ld+json; profile="https://www.w3.org/ns/activitystreams"'
    )
    media_type = "application/ld+json"
    format = "ld"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        data["@context"] = "https://www.w3.org/ns/activitystreams"
        return super().render(data, accepted_media_type, renderer_context)



class JrdRenderer(WebAppBaseRenderer):
    media_type = "application/jrd+json"
    format = "jrd"



class ActivityRenderer(renderers.BaseRenderer):
    """
    ActivitypubRenderer

    """

    accepted_media_type = (
        'application/json',
        'application/activity+json; profile="https://www.w3.org/ns/activitystreams"'
    )
    # media_type = [
    #    'application/activity+json',
    #    'application/ld+json',
    #   'application/json',  # Some clients use this
    #]
    media_type = "application/activity+json"
    format = "activity"


    encoder_class = encoders.JSONEncoder  # inherited from JSONRenderer
    ensure_ascii = not api_settings.UNICODE_JSON  # inherited from JSONRenderer
    compact = api_settings.COMPACT_JSON  # inherited from JSONRenderer
    strict = api_settings.STRICT_JSON  # same as JSONRenderer
    charset = None  # because it's a binary format

    def get_indent(self, accepted_media_type, renderer_context):
        if accepted_media_type:
            # If the media type looks like 'application/json; indent=4',
            # then pretty print the result.
            # Note that we coerce `indent=0` into `indent=None`.
            base_media_type, params = parse_header_parameters(accepted_media_type)
            with contextlib.suppress(KeyError, ValueError, TypeError):
                return zero_as_none(max(min(int(params["indent"]), 8), 0))
        # If 'indent' is provided in the context, then pretty print the result.
        # E.g. If we're being called by the BrowsableAPIRenderer.
        return renderer_context.get("indent", None)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        logger.debug("ActivityRenderer.render: media_type:" + str(accepted_media_type))
        if data is None:
            return b""
        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS

        # Make sure data includes the ActivityPub context if it doesn't already
        # if isinstance(data, dict) and '@context' not in data:
        #     data = {**data, '@context': 'https://www.w3.org/ns/activitystreams'}

        ret = json.dumps(
            data,
            cls=self.encoder_class,
            ensure_ascii=self.ensure_ascii,
            allow_nan=not self.strict,
            indent=indent,
            separators=separators,
        )

        # We always fully escape \u2028 and \u2029 to ensure we output JSON
        # that is a strict javascript subset.
        # See: https://gist.github.com/damncabbage/623b879af56f850a6ddc
        ret = ret.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        return ret.encode()
