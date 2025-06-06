from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

from .views import MastodonOAuth2Adapter


class MastoAccount(ProviderAccount):
    pass


class MastoProvider(OAuth2Provider):
    id = "mastodon"
    name = "Mastodon"

    account_class = MastoAccount
    oauth2_adapter_class = MastodonOAuth2Adapter

    def get_default_scope(self):
        return ["read", "write"]

    def extract_uid(self, data):
        return str(data["user_id"])

    def extract_common_fields(self, data):
        return dict(email=data.get("user"))

    def extract_email_addresses(self, data):
        from allauth.account.models import EmailAddress

        ret = []
        email = data.get("user")
        if email:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [MastoProvider]
