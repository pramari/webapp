# from django.core import serializers
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "npc.local")
django.setup()
from rest_framework import serializers # noqa: E402
from webapp.models import Actor # noqa: E402
# from rest_framework.renderers import JSONRenderer  # noqa: E402
from webapp.schema import schemas  # noqa: E402

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['@context', 'id', 'type', 'inbox', 'outbox', 'followers', 'following', 'liked']


if __name__ == "__main__":
    queryset = Actor.objects.filter(profile__isnull=False)
    single = queryset.filter(profile__user__username="andreas").get()
    ser = ActorSerializer(queryset, many=True)
    actor = ActorSerializer(single)
    from pyld import jsonld
    context = schemas['www.w3.org/ns/activitystreams']
    context_url = 'https://www.w3.org/ns/activitystreams'
    document = {
        "@context": 'https://www.w3.org/ns/activitystreams',
        # "@id": actor.data.pop('id'),
        **actor.data
    }
    print(f"Document: {document}")
    expanded = jsonld.expand(document)
    print(f"Expanded: {expanded}")
    print(f"Compacted: {jsonld.compact(document, context_url)}")
