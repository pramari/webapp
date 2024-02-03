from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_cookie


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
