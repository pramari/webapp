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

oauth2_login = OAuth2LoginView.adapter_view(MastoOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MastoOAuth2Adapter)
