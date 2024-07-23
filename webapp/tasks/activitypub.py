import json
import logging
import functools
import ipaddress
import socket

from celery import shared_task
from django.contrib.auth import get_user_model

# from taktivitypub.actor import Actor
# from taktivitypub import Follow

logger = logging.getLogger(__name__)
User = get_user_model()


@functools.lru_cache(maxsize=512)
def is_valid(url: str) -> bool:
    """
    Implements basic SSRF protection.
    Check if a remote object is valid
    Check if the URL is blocked
    """
    import urllib.parse
    from django.conf import settings

    if settings.DEBUG:  # pragma: no cover
        return True

    parsed = urllib.parse.urlparse(url)

    if parsed.scheme not in ["https"]:
        """
        Don't support HTTP
        """
        return False

    for blocked_hostname in settings.BLOCKED_SERVERS:  # noqa: E501
        if parsed.hostname == blocked_hostname or parsed.hostname.endswith(
            f".{blocked_hostname}"
        ):
            return False

    if not parsed.hostname or parsed.hostname.lower() in ["localhost"]:
        return False

    if parsed.hostname.endswith(".onion"):
        logger.warning(f"{url} is an onion service")
        return False

    try:
        ip_address = socket.getaddrinfo(
            parsed.hostname,
            parsed.port or (80 if parsed.scheme == "http" else 443),  # noqa: E501
        )[0][4][0]
        logger.debug(f"{ip_address=}")
    except socket.gaierror:  # [Errno -2] Name or service not known
        logger.info(f"rejecting not found invalid URL {url}")
        return False

    try:
        ip = ipaddress.ip_address(ip_address)
    except socket.gaierror:  # [Errno -2] Name or service not known
        logger.info(f"rejecting invalid IP {ip_address}")
        return False

    if ip.is_private:
        logger.info(f"rejecting private URL {url} -> {ip_address}")
        return False

    return True


@functools.lru_cache(maxsize=512)
def Fetch(url: str) -> dict:
    """
    Fetch a remote object
    """
    import django.core.exceptions
    from django.conf import settings
    from django.core.cache import cache

    if not settings.CACHES.get("default"):
        raise django.core.exceptions.ImproperlyConfigured(
            "ActivityPub Fetch requires configured cache."
        )

    if not is_valid(url):
        raise ValueError("Host/URL validation failed.")

    import requests

    headers = {
        "Content-type": "application/activity+json",
        "Accept": "application/activity+json",
    }

    return cache.get_or_set(
        url, requests.get(url, headers=headers).json(), 3600
    )  # noqa: E501


@shared_task
def getRemoteActor(id: str) -> dict:
    """
    Task to get details for a remote actor

    .. todo::
        - Add caching
        - Add error handling
        - Add tests
    """

    actor = Fetch(id)

    """
    .. todo::
        - Add error handling
        - Add tests
    """

    return actor

    """
    return Actor(
        id=actor.get("id"),
        inbox=actor.get("inbox"),
        outbox=actor.get("outbox"),  # noqa: E501
        publicKey=actor.get("publicKey", ""),
    )  # noqa: E501
    """


@shared_task
def requestFollow(localID: str, remoteID: str) -> bool:
    """
    Task to request a follow from a remote actor

    args:
        id: str: The id of the remote actor
    """
    from webapp.models import Actor as ActorModel
    from webapp.signature import signedRequest
    from webapp.signals import action

    localActor = ActorModel.objects.get(id=localID)
    remoteActor = getRemoteActor(remoteID)
    remoteActorObject = ActorModel.objects.get(id=remoteID)

    activity_id = action.send(
        sender=localActor, verb="Follow", target=remoteActorObject
    )[0][
        1
    ].get_activity_id()  # noqa: E501, BLK100

    message = json.dumps(
        {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"{activity_id}",
            "type": "Follow",
            "actor": localID,
            "object": remoteID,
        }
    )

    signed = signedRequest(  # noqa: F841,E501
        "POST", remoteActor.inbox, message, f"{localActor.id}#main-key"
    )  # noqa: F841,E501
    return True


@shared_task
def acceptFollow(message: dict) -> bool:
    """
    >>> from webapp.signature import signedRequest
    >>> r = signedRequest(
        "POST",
        "https://pramari.de/accounts/andreas/inbox",
        activitymessage,
        "https://pramari.de/@andreas#main-key"
    )
    """
    from webapp.signals import action
    from webapp.signature import signedRequest
    from webapp.models import Actor as ActorModel
    from django.contrib.site.models import Site

    base = Site.objects.get_current().domain

    remoteActor = getRemoteActor(message.get("actor"))
    remoteActorObject = ActorModel.objects.get(id=remoteActor.get("id"))
    localActorObject = ActorModel.objects.get(id=message.get("object"))

    o = action.send(
        sender=localActorObject, verb="Accept", target=remoteActorObject
    )  # noqa: E501, BLK100

    message = json.dumps(
        {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Accept",
            "id": f"https://{base}{o[0][1].id}",
            "actor": remoteActor.get("id"),
            "object": message,
        }
    )

    signed = signedRequest(  # noqa: F841,E501
        "POST",
        remoteActor.get("inbox"),
        message,
        f"{localActorObject.id}#main-key",  # noqa: E501
    )  # noqa: F841,E501

    return True


"""
@shared_task
def activitypub_send_task(user: User, message: str) -> Tuple[bool]:
    from Crypto.Hash import SHA256
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.PublicKey import RSA

    private_key = RSA.importKey(user.profile_set.get().private_key)
    # Sign the message
    signer = PKCS1_v1_5.new(private_key)

    actor = user.profile_set.get()
    date = datetime.datetime.now(datetime.timezone.utc)

    signed_string = f"(request-target): post /inbox\nhost: {user.socialaccount_set.first().extra_data['instance']}\ndate: {date}"  # noqa: E501
    # signature = keypair.sign(OpenSSL::Digest::SHA256.new, signed_string)
    digest = SHA256.new()
    digest.update(signed_string.encode("utf-8"))
    signature = signer.sign(digest)
    headers = {
        "keyId": f"{actor.get_actor_url()}",
        "headers": "(request-target) host date",
        "signature": f"{signature}",
    }
    import request

    return request.post(user.profile_set.get().get_inbox, headers=headers)
"""
