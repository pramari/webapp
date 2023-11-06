"""Views for Mastodon Auth."""
import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import MastoProvider


class MastoOAuth2Adapter(OAuth2Adapter):
    """OAuth2Adapter for Mastodon API."""

    provider_id = MastoProvider.id

    access_token_url = "https://mastodon.social/oauth/token"
    profile_url = "https://mastodon.social/oauth/access-tokens"

    @property
    def authorize_url(self):
        settings = self.get_provider().get_settings()
        url = settings.get(
            "AUTHORIZE_URL", "https://mastodon.social/oauth/authorize"
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


oauth2_login = OAuth2LoginView.adapter_view(MastoOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MastoOAuth2Adapter)
