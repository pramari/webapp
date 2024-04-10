"""
https://docs.python.org/3/library/typing.html
"""

import logging
import ipaddress
import functools
from socket import getaddrinfo

from urllib.parse import urlparse

import requests

from django.conf import settings

from taktivitypub.actor import Actor

from webapp.exceptions import (
    InvalidURLError,
)

logger = logging.getLogger(__name__)


def parseSignature(message: dict) -> dict:
    """ """

    return {
        "type": message.get("type"),
        "creator": message.get("creator"),
        "created": message.get("created"),
        "signatureValue": message.get("signatureValue"),
    }


def verifySignature(signature, publicKey) -> bool:
    """ """

    return True


def getRemoteActor(id: str) -> Actor:
    """ """

    headers = {
        "Content-type": "application/activity+json",
        "Accept": "application/activity+json",
    }
    actor = requests.get(id, headers=headers).json()
    return Actor(
        id=actor.get("id"),
        inbox=actor.get("inbox"),
        outbox=actor.get("outbox"),  # noqa: E501
        publicKey=actor.get("publicKey", ""),
    )  # noqa: E501


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


@functools.lru_cache(maxsize=512)
def check_url(url: str) -> None:
    logger.debug(f"check_url {url=}")
    if not is_url_valid(url):
        raise InvalidURLError(f'"{url}" is invalid')

    return None


"""
def fetch(
    url: str,
    params: dict[str, Any] | None = None,
    disable_httpsig: bool = False,
) -> APObject:
"""
"""
    .. todo::
        really, this shouldn't be httpx at all.
        that shouldn't be from microblog.pub at all.
    """
"""
    logger.info(f"Fetching {url} ({params=})")
    check_url(url)

    auth = httpx.BasicAuth(
        settings.AP_USER, settings.AP_PASS, settings.AP_CONTENT_TYPE
    )  # noqa: E501

    async with httpx.AsyncClient() as client:
        resp = client.get(
            url,
            headers={
                "User-Agent": settings.USER_AGENT,
                "Accept": settings.AP_CONTENT_TYPE,
            },
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
