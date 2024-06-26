import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from taktivitypub.actor import Actor

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def getRemoteActor(id: str) -> Actor:
    """
    Task to get details for a remote actor

    .. todo::
        - Add caching
        - Add error handling
        - Add tests
    """
    import requests

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


@shared_task
def accept_follow(actor: Actor, Object: Actor) -> bool:
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

    message = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Follow",
        "actor": actor.get_actor_url(),
        "object": Object.get_actor_url(),
    }

    signed = signedRequest(  # noqa: F841,E501
        "POST", actor.inbox, message, actor.privateKey
    )  # noqa: F841,E501

    action.send(sender=Actor, instance=Actor, verb="Accept")  # noqa: E501

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
