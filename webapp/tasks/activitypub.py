import json
import logging
import functools
import ipaddress
import socket

from celery import shared_task
from django.contrib.auth import get_user_model
from webapp.activity import ActivityObject

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
    from webapp.models import Actor
    from webapp.signature import signedRequest
    from webapp.signals import action

    localActor = Actor.objects.get(id=localID)
    remoteActor = getRemoteActor(remoteID)
    remoteActorObject = Actor.objects.get(id=remoteActor.get('id'))

    activity_id = action.send(
        sender=localActor, verb="Follow", target=remoteActorObject
    )[0][
        1
    ].id  # noqa: E501, BLK100

    print("Actor: ", localActor)
    print("Type: ", type(localActor))
    print("Actor Following: ", localActor.follows)
    print("Type: ", type(localActor.follows))


    message = json.dumps(
        {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"{activity_id}",
            "type": "Follow",
            "actor": localID,
            "object": remoteID,
        }
    )
    localActor.follows.add(remoteActorObject)  # remember we follow this actor

    signed = signedRequest(  # noqa: F841,E501
        "POST", remoteActor.get('inbox'), message, f"{localActor.id}#main-key"
    )  # noqa: F841,E501
    return True


@shared_task
def acceptFollow(inbox: str, activity: ActivityObject, accept_id: str) -> bool:
    """
    >>> from webapp.signature import signedRequest
    >>> r = signedRequest(
        "POST",
        "https://pramari.de/accounts/andreas/inbox",
        activitymessage,
        "https://pramari.de/@andreas#main-key"
    )
    """
    from webapp.signature import signedRequest
    from django.contrib.sites.models import Site

    base = Site.objects.get_current().domain

    message = json.dumps(
        {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Accept",
            "id": f"https://{base}/{accept_id}",
            "actor": activity.object,
            "object": activity.toDict(),
        }
    )
    logger.error(f"acceptFollow to {activity.actor}")
    logger.error(f"with message: {message=}")

    signed = signedRequest(  # noqa: F841,E501
        "POST",
        inbox,
        message,
        f"{activity.object}#main-key",  # noqa: E501
    )  # noqa: F841,E501

    if signed.ok:
        return True
    return False


@shared_task
def sendLike(localActor: str, object: str) -> bool:
    """
    .. py:function:: sendLike(localActor: dict, object: str) -> bool
    .. todo::
        - Add tests
        - Implement
    """
    from webapp.signature import signedRequest
    from webapp.tasks.activitypub import Fetch

    if not isinstance(localActor, str):
        raise ValueError("localActor must be a string")
    if not isinstance(object, str):
        raise ValueError("object must be a string")

    fetched = Fetch(object)
    remote = fetched.get("attributedTo")
    actor_inbox = Fetch(remote).get("inbox")
    """
    {'@context': ['https://www.w3.org/ns/activitystreams', {'ostatus': 'http://ostatus.org#', 'atomUri': 'ostatus:atomUri', 'inReplyToAtomUri': 'ostatus:inReplyToAtomUri', 'conversation': 'ostatus:conversation', 'sensitive': 'as:sensitive', 'toot': 'http://joinmastodon.org/ns#', 'votersCount': 'toot:votersCount'}], 'id': 'https://23.social/users/andreasofthings/statuses/112826215633359303', 'type': 'Note', 'summary': None, 'inReplyTo': None, 'published': '2024-07-21T19:50:25Z', 'url': 'https://23.social/@andreasofthings/112826215633359303', 'attributedTo': 'https://23.social/users/andreasofthings', 'to': ['https://www.w3.org/ns/activitystreams#Public'], 'cc': ['https://23.social/users/andreasofthings/followers'], 'sensitive': False, 'atomUri': 'https://23.social/users/andreasofthings/statuses/112826215633359303', 'inReplyToAtomUri': None, 'conversation': 'tag:23.social,2024-07-21:objectId=4978426:objectType=Conversation', 'content': '<p>Harris/Ocasio-Cortez</p>', 'contentMap': {'en': '<p>Harris/Ocasio-Cortez</p>'}, 'attachment': [], 'tag': [], 'replies': {'id': 'https://23.social/users/andreasofthings/statuses/112826215633359303/replies', 'type': 'Collection', 'first': {'type': 'CollectionPage', 'next': 'https://23.social/users/andreasofthings/statuses/112826215633359303/replies?min_id=112826217149903948&page=true', 'partOf': 'https://23.social/users/andreasofthings/statuses/112826215633359303/replies', 'items': ['https://23.social/users/andreasofthings/statuses/112826217149903948']}}}  # noqa: E501
    """

    message = json.dumps(
        {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Like",
            "actor": localActor,
            "object": object,
        }
    )

    print("sending like")
    print(f"to: {actor_inbox}")
    print(message)
    signed = signedRequest(  # noqa: F841,E501
        "POST", actor_inbox, message, f"{localActor}#main-key"
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
