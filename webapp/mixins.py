from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_cookie

from django.http import JsonResponse  # , HttpResponseRedirect

# from django.core.exceptions import ImproperlyConfigured
# from django.urls import reverse


class CacheMixin(object):
    cache_timeout = 60

    def _get_cache_timeout(self):
        return self.cache_timeout

    @method_decorator(vary_on_cookie)
    def dispatch(self, *args, **kwargs):
        return cache_page(self._get_cache_timeout())(
            super(CacheMixin, self).dispatch
        )(  # noqa: E501
            *args, **kwargs
        )


class RequireContentTypeMixinMixin(object):
    """
    A mixin that returns a JSON-LD response if the request
    specifies 'application/activity+json' in the Accept header.

    This mixin is intended to be used with Django Class Based Views.

    to_jsonld() is a method that should be implemented by the class.

    :param content_type: The content type to check for in the Accept header. Defaults to 'application/activity+json'.

    Example usage:
        class SomeView(JsonLDMixin, View):
            content_type = "application/activity+json"
            def to_jsonld(self, request, *args, **kwargs):
                return {
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "type": "Note",
                    "content": "This is a note",
                }
    """

    content_type = "application/activity+json"

    def to_jsonld(self, *args, **kwargs):
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        if (
            "Accept" in request.headers
            and "application/activity+json"
            in request.headers.get("Accept")  # noqa: E501
        ):
            return JsonResponse(
                self.to_jsonld(request, *args, **kwargs),
                content_type="application/activity+json",
            )
        return super().get(request, *args, **kwargs)
