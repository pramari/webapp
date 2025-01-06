import logging

from typing import Tuple

from celery import shared_task
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialToken, SocialApp

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task
def getAppAndAccessToken(
    user: User, provider: str = "google"
) -> Tuple[SocialApp, SocialToken]:
    try:
        app = SocialApp.objects.get(provider=provider)
    except SocialApp.DoesNotExist:
        app = None

    try:
        accessToken = SocialToken.objects.get(  # pylint: disable=no-member
            account__user=user, account__provider=app  # provider
        )
    except SocialToken.DoesNotExist:
        accessToken = None

    return (app, accessToken)


def genKeyPair() -> Tuple[str, str]:
    from cryptography.hazmat.primitives import (
        serialization as crypto_serialization,
    )  # noqa: E501
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import (
        default_backend as crypto_default_backend,
    )  # noqa: E501

    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048,  # noqa: E501
    )

    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption(),
    ).decode("utf-8")

    public_key = (
        key.public_key()
        .public_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )
    return (private_key, public_key)


@shared_task
def generateProfileKeyPair(
    modeladmin: str, request, queryset, verbose=True
) -> bool:  # noqa: E501
    """
    Wrap `genKeyPair` in a Celery task to generate key pairs
    for all users in the queryset.
    """
    """
    from cryptography.hazmat.primitives import (
        serialization as crypto_serialization,
    )  # noqa: E501
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import (
        default_backend as crypto_default_backend,
    )  # noqa: E501
    """
    for user in queryset.all():
        """
        key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=65537,
            key_size=2048,  # noqa: E501
        )

        user.profile.private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption(),
        ).decode("utf-8")

        user.profile.public_key = (
            key.public_key()
            .public_bytes(
                crypto_serialization.Encoding.PEM,
                crypto_serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("utf-8")
        )
        """
        (
            user.profile.private_key_pem,
            user.profile.public_key_pem,
        ) = genKeyPair()
        """
        Optimize below?
        """
        user.profile.save()
        user.save()
        user.profile.save()
    return True
