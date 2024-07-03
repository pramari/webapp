from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_cookie

from django.http import JsonResponse, HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse


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


class JsonLDMixin(object):
    redirect_to = None

    def get_redirect_url(self, *args, **kwargs):
        """
        Get the specified redirect_to url
        """

        if not self.redirect_to:
            raise ImproperlyConfigured(
                "no url to redirect to. please specify a redirect url"
            )

        return reverse(self.redirect_to, kwargs={"slug": kwargs.get("slug")})

    def to_jsonld(self, *args, **kwargs):
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        if (
            "Accept" in request.headers and "application/activity+json" in request.headers.get("Accept")  # noqa: E501
        ):
            return JsonResponse(
                self.to_jsonld(request, *args, **kwargs),
                content_type="application/activity+json",
            )
        else:
            if self.redirect_to:
                return HttpResponseRedirect(
                    self.get_redirect_url(request, *args, **kwargs)
                )  # noqa: E501
            else:
                return super().get(request, *args, **kwargs)
