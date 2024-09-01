# from django.core import serializers
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "npc.local")
django.setup()
from rest_framework import serializers
from webapp.models import Actor
from rest_framework.renderers import JSONRenderer


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['type', 'inbox', 'outbox', 'followers', 'following', 'liked']


if __name__ == "__main__":
    queryset = Actor.objects.filter(profile__isnull=False)
    print(queryset)
    single = queryset.filter(profile__user__username="andreas")
    print(single)
    ser = ActorSerializer(queryset, many=True)
    print(ser)
    ser = ActorSerializer(single)
    print(ser)
    print(JSONRenderer().render(ser.data))
