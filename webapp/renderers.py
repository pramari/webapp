"""renderers.py

    .. seealso:: https://www.w3.org/ns/activitystreams
    
    .. seealso::
    https://www.django-rest-framework.org/api-guide/renderers/#custom-renderers

    Returns:
        _type_: _description_
"""

from rest_framework import renderers

class JsonLDRenderer(renderers.BaseRenderer):
    """JsonLDRenderer

    Args:
        renderers (JsonLDRenderer): Renders JSON-LD data

    Returns:
        JsonLD: Added Context to JSON-LD data
    """
    media_type = 'application/ld+json; profile="https://www.w3.org/ns/activitystreams"'
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        data['@context'] = "https://www.w3.org/ns/activitystreams"
        return data.encode(self.charset)