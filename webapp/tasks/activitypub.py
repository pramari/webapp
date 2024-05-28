import datetime
import logging

from typing import Tuple

from celery import shared_task
from django.contrib.auth import get_user_model
from webapp.models import Action
from taktivitypub.actor import Actor

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def getRemoteActor(id: str) -> Actor:
    """
    Task to get details for a remote actor
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
def accept_follow(user: User, actor: Actor, activity: Action) -> bool:
    import requests  # noqa: F401
    from requests_http_signature import (
        HTTPSignatureAuth,  # noqa: F401
        algorithms,  # noqa: F401
    )  # noqa: F401, E501

    auth = HTTPSignatureAuth(
        key=user.key,
        key_id=user.key,
        signature_algorithm=algorithms.HMAC_SHA256,  # noqa: E501
    )
    requests.post(actor.inbox, auth=auth)

    return True


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
