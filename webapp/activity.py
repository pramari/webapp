"""
https://docs.python.org/3/library/typing.html
"""

import logging
import ipaddress
import functools

from typing import Any
from socket import getaddrinfo

from urllib.parse import urlparse

import requests

from django.conf import settings
from django.http import HttpRequest

from taktivitypub.actor import Actor
from taktivitypub.activity import Activity

from webapp.exceptions import (
    InvalidURLError,
    ObjectIsGoneError,
    ObjectUnavailableError,
    ObjectNotFoundError,
)

from http_message_signatures import HTTPSignatureKeyResolver

logger = logging.getLogger(__name__)


class ActorKeyResolver(HTTPSignatureKeyResolver):
    def resolve_public_key(self, key_id):
        from webapp.tasks import getRemoteActor

        assert isinstance(key_id, str)
        actor = getRemoteActor(key_id)
        return actor["publicKey"]["publicKeyPem"]


def parseSignature(request: HttpRequest) -> bool:
    """
    Parse the signature from the message.

    Request: {
        'Signature': 'keyId="https://23.social/users/andreasofthings#main-key",algorithm="rsa-sha256",headers="(request-target) host date digest content-type",signature="e5Vj4XBt9B/TJSI4iJPDW3NtAXtOM8Z6y0j72uglfSi/R1xVwUvGcgu/r0h5yaf8e5weBZcuQ7t4ztMJfQGhol2weRWqFiC5vN1SkJTnen669sX0z6JPR/9FV9piEeSLCGHdW1wscR0c1XIQNciciPB8RrgouEQxmOxPCvlXFxqQeAVRH82d5UObSU9XQOx9/j8et/lCPegQuDM00l6qmhAAwqX7UnVDrNUJgN3eYcJpOMGfGNeymdZwf3j8/CAdQGgQPfzuNmDHvy4Wo79BZV4ud9mkVquEAh7RagfwIQRUtM/mI2i2qGrXwnpjwhOgxJkjoG7Fc18qvzuT3nQfQg=="', # noqa: E501
    """

    from requests_http_signature import HTTPSignatureAuth

    result = HTTPSignatureAuth.verify(request, key_resolver=ActorKeyResolver())
    return result


"""
class ActivityBase(dict):
    def __init__(self, incoming: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def is_ok(self) -> bool:
        ""
        .. todo::
            probably not. need to implement.
        ""
        return True
"""

"""
class ActivitySignature(dict):
    def __init__(
        self, type: str, creator: str, created: str, signatureValue: str
    ) -> None:
        self.type = type
        self.creator = creator
        self.created = created
        self.signatureValue = signatureValue

    def is_valid(self) -> bool:
        return True
"""


"""
class ActivityObject(ActivityBase):
    context = ""
    type = ""
    actor = ""
    to = []
    signature = {}  # noqa: E841

    def __init__(self, *args, **kwargs) -> None:
        self.signature = ActivitySignature(kwargs.pop("signature", {}))
        super().__init__(*args, **kwargs)
"""


"""
https://git.sr.ht/~tsileo/microblog.pub/tree/v2/item/app/utils/url.py
"""


@functools.lru_cache(maxsize=256)
def is_hostname_blocked(hostname: str) -> bool:
    for blocked_hostname in settings.BLOCKED_SERVERS:  # noqa: E501
        if hostname == blocked_hostname or hostname.endswith(
            f".{blocked_hostname}"
        ):  # noqa: E501
            return True
    return False


@functools.lru_cache(maxsize=512)
def is_url_valid(url: str) -> bool:
    """Implements basic SSRF protection."""
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        return False

    if settings.DEBUG:  # pragma: no cover
        return True

    if not parsed.hostname or parsed.hostname.lower() in ["localhost"]:
        return False

    if is_hostname_blocked(parsed.hostname):
        logger.warning(f"{parsed.hostname} is blocked")
        return False

    if parsed.hostname.endswith(".onion"):
        logger.warning(f"{url} is an onion service")
        return False

    ip_address = getaddrinfo(
        parsed.hostname,
        parsed.port or (80 if parsed.scheme == "http" else 443),  # noqa: E501
    )
    logger.debug(f"{ip_address=}")

    if ipaddress.ip_address(ip_address).is_private:
        logger.info(f"rejecting private URL {url} -> {ip_address}")
        return False

    return True


def fetch(
    url: str,
    params: dict[str, Any] | None = None,
    disable_httpsig: bool = False,
) -> Actor | Activity:
    """
    .. todo::
        really, this shouldn't be httpx at all.
        that shouldn't be from microblog.pub at all.
    """

    logger.info(f"Fetching {url} ({params=})")
    if not is_url_valid(url):
        raise InvalidURLError(f"'{url} is invalid")

    auth = requests.auth.HTTPBasicAuth(
        settings.AP_USER, settings.AP_PASS, settings.AP_CONTENT_TYPE
    )

    headers = {
        "User-Agent": settings.USER_AGENT,
        "Accept": settings.AP_CONTENT_TYPE,
    }

    with requests.Session() as session:
        resp = session.get(
            url,
            headers=headers,
            params=params,
            auth=None if disable_httpsig else auth,
        )

        # Special handling for deleted object
        if resp.status_code == 410:
            raise ObjectIsGoneError(url, resp)
        elif resp.status_code in [401, 403]:
            raise ObjectUnavailableError(url, resp)
        elif resp.status_code == 404:
            raise ObjectNotFoundError(url, resp)


"""
    async with httpx.AsyncClient() as client:
        resp = client.get(
            url,
            headers=headers,
            params=params,
            follow_redirects=True,
            auth=None if disable_httpsig else auth,
        )

    # Special handling for deleted object
    if resp.status_code == 410:
        raise ObjectIsGoneError(url, resp)
    elif resp.status_code in [401, 403]:
        raise ObjectUnavailableError(url, resp)
    elif resp.status_code == 404:
        raise ObjectNotFoundError(url, resp)

    try:
        resp.raise_for_status()
    except httpx.HTTPError as http_error:
        raise FetchError(url, resp) from http_error

    try:
        return resp.json()
    except json.JSONDecodeError:
        raise NotAnObjectError(url, resp)
    """
