"""
# Ruby:
require 'http'
require 'openssl'

document      = File.read('create-hello-world.json')
date          = Time.now.utc.httpdate
keypair       = OpenSSL::PKey::RSA.new(File.read('private.pem'))
signed_string = "(request-target): post /inbox\nhost: mastodon.social\ndate: #{date}"
signature     = Base64.strict_encode64(keypair.sign(OpenSSL::Digest::SHA256.new, signed_string))
header        = 'keyId="https://my-example.com/actor",headers="(request-target) host date",signature="' + signature + '"'

HTTP.headers({ 'Host': 'mastodon.social', 'Date': date, 'Signature': header })
    .post('https://mastodon.social/inbox', body: document)
"""

import datetime

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

date = datetime.datetime.now(datetime.timezone.utc)

