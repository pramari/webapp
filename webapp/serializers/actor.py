# from django.core import serializers
from rest_framework import serializers

from webapp.models import Actor

class ActorSerializer(serializers.Serializer):
    class Meta:
        model = Actor
        fields = ['id', 'type', 'inbox', 'outbox', 'followers', 'following', 'liked']

    def create(self, validated_data):
        return Actor.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.actor_name = validated_data.get('actor_name', instance.actor_name)
        instance.actor_age = validated_data.get('actor_age', instance.actor_age)
        instance


if __name__ == "__main__":
    print("This is the actor module")
    print(serializers.serialize("json", Actor.objects.all()))
