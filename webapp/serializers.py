#!/usr/bin/python3
"""
serializers.py.

(De-)Serializers of objects.
"""


from rest_framework import serializers


class AttributeSerializer(serializers.Serializer):
    """
    {
        'billingAccountId': '019322-946E63-D23975',
        'budgetId': 'ade28095-2bab-4433-b504-f734dfc224d0',
        'schemaVersion': '1.0'
    },
    """

    billingAccountId = serializers.CharField(max_length=200)
    budgetId = serializers.CharField(max_length=200)
    schemaVersion = serializers.CharField(max_length=200)

    def create(self, **kwargs):
        pass


class MessageSerializer(serializers.Serializer):
    """
    {
        'attributes': 'see AttributeSerializer'
        'data':
        'ewogICJidWRnZXREaXNwbGF5TmFtZSI6ICJEZWZhdWx0IiwKICAiY29zdEFtb3VudCI6IDAuMDcsCiAgImNvc3RJbnRlcnZhbFN0YXJ0IjogIjIwMTktMDctMDFUMDc6MDA6MDBaIiwKICAiYnVkZ2V0QW1vdW50IjogMTIuMCwKICAiYnVkZ2V0QW1vdW50VHlwZSI6ICJTUEVDSUZJRURfQU1PVU5UIiwKICAiY3VycmVuY3lDb2RlIjogIkVVUiIKfQ==',
        'messageId': '603388362718701',
        'message_id': '603388362718701',
        'publishTime': '2019-07-02T11:33:08.697Z',
        'publish_time': '2019-07-02T11:33:08.697Z'
    },
    """

    attributes = AttributeSerializer()
    data = serializers.CharField(max_length=1024)
    messageId = serializers.CharField(max_length=128)
    message_id = serializers.CharField(max_length=128)
    publishTime = serializers.CharField(max_length=128)
    publish_time = serializers.CharField(max_length=128)


class BudgetSerializer(serializers.Serializer):
    """
    bla = {
        'message': 'see MessageSerializer'
        'subscription': 'projects/pramari-de/subscriptions/app-engine'
    }
    """

    message = MessageSerializer()
    subscription = serializers.CharField(max_length=128)
