from rest_framework import serializers
from webapp.activitypub.models import Action


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['id', 'activity_id', ]
