from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import MastoProvider


urlpatterns = default_urlpatterns(MastoProvider)
