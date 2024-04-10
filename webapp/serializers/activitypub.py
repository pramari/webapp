#!/usr/bin/python3
"""
serializers.py.

(De-)Serializers of objects.
"""


from rest_framework import serializers

"""
{'@context': 'https://www.w3.org/ns/activitystreams', 'id':
 'https://mastodon.social/users/future_apocalypse#delete', 'type': 'Delete',
 'actor': 'https://mastodon.social/users/future_apocalypse', 'to':
 ['https://www.w3.org/ns/activitystreams#Public'], 'object':
 'https://mastodon.social/users/future_apocalypse', 'signature': {'type':
                                                                  'RsaSignature2017',
                                                                  'creator':
                                                                  'https://mastodon.social/users/future_apocalypse#main-key',
                                                                  'created':
                                                                  '2024-03-06T09:25:21Z',
                                                                  'signatureValue':
                                                                  'tL21ea49VXyJQkGQ5UiIZaV6vZa5oKDoIdoSw6bLWTiFXcRsyufWGKaEm6Joy1HVfMIX/xBpSYPdEW3toifxNXXKDviooIPgYrC+ewvdgGluB5KVwhsyOVZngrBM44cJbc3eepgY2GfauOQR6h/+goi7BffC2WBpBSOCYuQJ2pDm5OyE0ZfgHsnpIAMUPZWmaZUMxAb4+Jj9VUaXNIpc4ghDTOgoUXhBkPf0lFBhS0cerH9Lsv2j8x15746Z0HzwFa1a0ialRnPLfGsLD0BfD1c7693ldAKu6BXrGJclurlFbyv+JPKCKF2TICguDQVl6zb9Pet2gWPmBEv1YOF0DA=='}}  # noqa: E501
"""


class ActivitySignatureSerializer(serializers.Serializer):
    """
    De-/Serialize Activity Signatures.
    """

    type = serializers.CharField(max_length=128)
    creator = serializers.CharField(max_length=128)
    created = serializers.DateTimeField()
    signatureValue = serializers.CharField(max_length=1024)


class ActivitySerializer(serializers.Serializer):
    """
    Deserializes the activity message.
    """

    context = serializers.CharField(max_length=128, required=False)
    id = serializers.CharField(max_length=128)
    type = serializers.CharField(max_length=128)
    actor = serializers.CharField(max_length=128)
    to = serializers.CharField(max_length=128)
    object = serializers.CharField(max_length=128)


class ActivityMessage(object):
    """
    Activity Message Object.
    """

    def __init__(self, context, id, type, actor, to, object):
        """
        Initialize the object.
        """
        self.context = context
        self.id = id
        self.type = type
        self.actor = actor
        self.to = to
        self.object = object
        self.signature = None

    def __str__(self):
        """
        String representation of the object.
        """
        return f"Context: {self.context}, ID: {self.id}, Type: {self.type}, Actor: {self.actor}, To: {self.to}, Object: {self.object}"  # noqa: E501
