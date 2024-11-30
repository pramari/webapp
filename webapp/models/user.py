import logging
from django.contrib.auth.models import AbstractUser  # type: ignore
from allauth.account.models import EmailAddress

logger = logging.getLogger(__name__)

try:
    pass
    # from allauth.socialaccount.models import SocialToken, SocialApp,
    # from allauth.socialaccount.models import SocialAccount  # type
except ImportError:
    logger.error("Cannot import SocialToken")


class User(AbstractUser):
    """
    Custom User Model.

    Configure in `settings.py`:

        `AUTH_USER_MODEL = "webapp.User"`

    Model extends AbstractUser to store information
    specific to an APC User. Core function is to return
    information about verified status and social account
    details.
    """

    @property
    def is_verified(self) -> bool:
        """
        Return Verification Status.

        :return: True if any of the registered email addresses have been
            verified. Filter all `EmailAddress`es for this user `self`.

        """

        queryset = EmailAddress.objects.filter(  # noqa: E501
            user=self, verified=True, primary=True
        )
        return queryset.count() > 0

    # public = models.BooleanField(default=False)  # -> Profile
    # consent = models.BooleanField(default=False) # -> Profile

    @property
    def services(self) -> list[str]:
        """
        List all services a user has associated.

        :return: List of strings.

        """
        try:
            accounts = self.socialaccount_set.all()
        except self.socialaccount_set.model.DoesNotExist:
            return []
        return [f"{account.provider}" for account in accounts]  # accounts

    @property
    def get_absolute_url(self):
        """
        Default Django Method/Best Practice
        """
        from django.urls import reverse

        return reverse(
            "user-detail",
        )
