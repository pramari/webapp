from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.timezone import now
import uuid


import logging
logger = logging.getLogger(__name__)


class Note(models.Model):
    """
    Activity Streams 2.0

    Type: Note 
        {
        'id': 'https://23.social/users/andreasofthings/statuses/112728133944821188', 
        'type': 'Note', 
        'summary': None, 
        'inReplyTo': None, 
        'published': '2024-07-04T12:06:57Z', 
        'url': 'https://23.social/@andreasofthings/112728133944821188', 
        'attributedTo': 'https://23.social/users/andreasofthings', 
        'to': ['https://www.w3.org/ns/activitystreams#Public'], 
        'cc': ['https://23.social/users/andreasofthings/followers'], 
        'sensitive': False, 
        'atomUri': 'https://23.social/users/andreasofthings/statuses/112728133944821188', 
        'inReplyToAtomUri': None, 
        'conversation': 'tag:23.social,2024-07-04:objectId=4444254:objectType=Conversation', 
        'content': '<p>I implemented http signatures (both sign and verify) for the fediverse.</p><p>In python.</p><p>I feel like I made fire.</p>', 
        'contentMap': {'en': '<p>I implemented http signatures (both sign and verify) for the fediverse.</p><p>In python.</p><p>I feel like I made fire.</p>'}, 
        'attachment': [], 
        'tag': [], 
        'replies': {
            'id': 'https://23.social/users/andreasofthings/statuses/112728133944821188/replies', 
            'type': 'Collection', 
            'first': {
                'type': 'CollectionPage', 
                'next': 'https://23.social/users/andreasofthings/statuses/112728133944821188/replies?only_other_accounts=true&page=true', 
                'partOf': 'https://23.social/users/andreasofthings/statuses/112728133944821188/replies', 
                'items': []
            }
        }
    }  # noqa: E501

    """

    class Meta:
        verbose_name = _("Note (Activity Streams 2.0)")
        verbose_name_plural = _("Notes (Activity Streams 2.0)")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    remoteID = models.URLField(blank=True, null=True, db_index=True)

    content = models.TextField()
    attributedTo = models.ForeignKey(Actor, on_delete=models.CASCADE, null=True)
    contentMap = models.JSONField(blank=True, null=True)

    published = models.DateTimeField(default=now, db_index=True)
    updated = models.DateTimeField(default=now, db_index=True)

    public = models.BooleanField(default=True, db_index=True)
    sensitive = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse("note-detail", args=[self.id])

    @property
    def type(self):
        return "Note"
    
    @property
    def summary(self):
        return self.summary