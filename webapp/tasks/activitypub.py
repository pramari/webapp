import datetime
import logging

from typing import Tuple

from celery import shared_task
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


"""
# Ruby:
require 'http'
require 'openssl'

document      = File.read('create-hello-world.json')
date          = Time.now.utc.httpdate
keypair       = OpenSSL::PKey::RSA.new(File.read('private.pem'))
signed_string = "(request-target): post /inbox\nhost: mastodon.social\ndate: #{date}"  # noqa: E501
signature     = Base64.strict_encode64(keypair.sign(OpenSSL::Digest::SHA256.new, signed_string))  # noqa: E501
header        = 'keyId="https://my-example.com/actor",headers="(request-target) host date",signature="' + signature + '"'  # noqa: E501

HTTP.headers({ 'Host': 'mastodon.social', 'Date': date, 'Signature': header })
    .post('https://mastodon.social/inbox', body: document)
"""


message = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "id": "https://my-example.com/create-hello-world",
    "type": "Create",
    "actor": "https://my-example.com/actor",
    "object": {
        "id": "https://my-example.com/hello-world",
        "type": "Note",
        "published": "2018-06-23T17:17:11Z",
        "attributedTo": "https://my-example.com/actor",
        "inReplyTo": "https://mastodon.social/@Gargron/100254678717223630",
        "content": "<p>Hello world</p>",
        "to": "https://www.w3.org/ns/activitystreams#Public",
    },
}


@shared_task
def activitypub_send_task(user: User, message: message) -> Tuple[bool]:
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
