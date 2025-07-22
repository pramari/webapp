# from django.core import serializers
import os
import django

from rest_framework import serializers  # noqa: E402
from webapp.activitypub.models import Actor  # noqa: E402
from webapp.activitypub.schema import schemas  # noqa: E402


class ActorSerializer(serializers.ModelSerializer):
    """
    serializer.ModelSerializer:

        .to_representation() - Override this to support serialization, for read operations.
        .to_internal_value() - Override this to support deserialization, for write operations.

    .. example::
        {
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
        return actor.id

    def get_preferred_username(self, actor):
        return actor.profile.user.username

    def get_name(self, actor):
        return actor.profile.user.username

    def get_summary(self, actor):
        return actor.profile.bio

    def get_published(self, actor):
        return actor.profile.user.date_joined.isoformat()

    def get_endpoints(self, actor):
        """
        get_endpoints returns the endpoints for the actor.
        """
        return   {
          "sharedInbox": "https://pramari.de/inbox"
        }

    def to_representation(self, instance):
        """
        .to_representation() - Override this to support serialization, for read operations.
        """
        data = super().to_representation(instance)
        # data["@context"] = "https://www.w3.org/ns/activitystreams"
        return data

    def to_internal_value(self, data):
        """
        .to_internal_value() - Override this to support deserialization, for write operations.
        """
        return super().to_internal_value(data)

    url = serializers.SerializerMethodField("get_url")
    publicKey = serializers.SerializerMethodField("get_public_key")
    preferredUsername = serializers.SerializerMethodField("get_preferred_username")
    name = serializers.SerializerMethodField("get_name")
    summary = serializers.SerializerMethodField("get_summary")
    published = serializers.SerializerMethodField("get_published")
    endpoints = serializers.SerializerMethodField("get_endpoints")

    class Meta:
        model = Actor
        fields = [
            "id",
            "type",
            "preferredUsername",
            "name",
            "summary",
            "inbox",
            "outbox",
            "followers",
            "following",
            "liked",
            "publicKey",
            "url",
            "published",
            "endpoints",
            "manuallyApprovesFollowers",
            "discoverable",
        ]



if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "npc.local")
    django.setup()

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
    # expanded = jsonld.expand(document)
    # print(f"Expanded: {expanded}")
    # print(f"Compacted: {jsonld.compact(document, context_url)}")
    print(f"Compacted: {jsonld.compact(actor.data, context_url)}")
