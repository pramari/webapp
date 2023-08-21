"""Views for Hubspot API."""
import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import HSProvider


class HSOAuth2Adapter(OAuth2Adapter):
    """OAuth2Adapter for Hubspot API v3."""

    provider_id = HSProvider.id

    access_token_url = "https://api.hubapi.com/oauth/v1/token"
    profile_url = "https://api.hubapi.com/oauth/v1/access-tokens"

    @property
    def authorize_url(self):
        settings = self.get_provider().get_settings()
        url = settings.get(
            "AUTHORIZE_URL", "https://app.hubspot.com/oauth/authorize"
        )
        return url

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            "{0}/{1}".format(self.profile_url, token.token), headers=headers
        )
        response.raise_for_status()
        extra_data = response.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(HSOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(HSOAuth2Adapter)
