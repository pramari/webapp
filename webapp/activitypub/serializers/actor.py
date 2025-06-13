# from django.core import serializers
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "npc.local")
django.setup()
from rest_framework import serializers  # noqa: E402
from webapp.activitypub.models import Actor  # noqa: E402
from webapp.activitypub.schema import schemas  # noqa: E402


class ActorSerializer(serializers.ModelSerializer):
    """
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
        ],
        "id": actor.id,
        "type": "Person",
        "name": actor.profile.user.username,
        "preferredUsername": actor.profile.user.username,
        "summary": actor.profile.bio,
        "inbox": actor.inbox,
        "outbox": actor.outbox,
        "followers": actor.followers,
        "following": actor.following,
        "liked": actor.liked,
        "url": self.get_object().get_absolute_url,
        "manuallyApprovesFollowers": False,
        "discoverable": False,
        "indexable": False,
        "published": actor.profile.user.date_joined.isoformat(),
        "publicKey": {
            "id": actor.keyID,
            "owner": actor.id,
            "publicKeyPem": actor.profile.public_key_pem,
        },
        "image": {  # background image
            "type": "Image",
            "mediaType": "image/jpeg",
            "url": actor.profile.imgurl,
        },  # noqa: E501
        "icon": {
            "type": "Image",
            "mediaType": "image/png",
            "url": actor.profile.imgurl,
        },  # noqa: E501
    }
    """

    def get_public_key(self, actor):
        return {
            "id": actor.keyID,
            "owner": actor.id,
            "publicKeyPem": actor.profile.public_key_pem,
        }

    def get_url(self, actor):
        return (actor.id,)

    def get_preferred_username(self, actor):
        return actor.profile.user.username

    url = serializers.SerializerMethodField("get_url")
    public_key = serializers.SerializerMethodField("get_public_key")
    preferred_username = serializers.SerializerMethodField("get_preferred_username")

    class Meta:
        model = Actor
        fields = [
            "id",
            "type",
            "preferred_username",
            "inbox",
            "outbox",
            "followers",
            "following",
            "liked",
            "public_key",
            "url",
        ]


if __name__ == "__main__":
    queryset = Actor.objects.filter(profile__isnull=False)
    single = queryset.filter(profile__user__username="andreas").get()
    ser = ActorSerializer(queryset, many=True)
    actor = ActorSerializer(single)
    from pyld import jsonld

    context = schemas["www.w3.org/ns/activitystreams"]
    context_url = "https://www.w3.org/ns/activitystreams"
    document = {
        "@context": "https://www.w3.org/ns/activitystreams",
        # "@id": actor.data.pop('id'),
        **actor.data,
    }
    print(f"Document: {document}")
    expanded = jsonld.expand(document)
    print(f"Expanded: {expanded}")
    print(f"Compacted: {jsonld.compact(document, context_url)}")
