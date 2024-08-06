# from django.core import serializers
from rest_framework import serializers

from webapp.models import Actor

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'type', 'inbox', 'outbox', 'followers', 'following', 'liked']


if __name__ == "__main__":
    print("This is the actor module")
    print(serializers.serialize("json", Actor.objects.all()))
