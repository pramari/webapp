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
    profile_url = "https://mastodon.social/oauth/token"
    authorize_url = "https://mastodon.social/oauth/authorize"

    def complete_login(self, request, app, access_token, **kwargs):
        # headers = {"Content-Type": "application/json"}
        response = requests.get(
            self.profile_url, params={"access_token": access_token}
        )  # noqa: E501
        extra_data = response.json()
        return self.get_provider().sociallogin_from_response(
            request, extra_data
        )  # noqa: E501

        response.raise_for_status()
        extra_data = response.json()
        return self.get_provider().sociallogin_from_response(
            request, extra_data
        )  # noqa: E501


oauth2_login = OAuth2LoginView.adapter_view(MastoOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MastoOAuth2Adapter)
