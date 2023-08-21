#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
Models for `Angry Planet Cloud`.

At the time, this file exists for `Django` only, however, this
may be the right home for an `Usermodel` in the future.
"""

from django.contrib.auth.models import AbstractUser       # type: ignore
from django.db.models.signals import pre_save, post_save  # type: ignore
from django.dispatch import receiver                      # type: ignore
from django.db import models                              # type: ignore
from django.urls import reverse

from allauth.account.models import EmailAddress           # type: ignore

import logging


logger = logging.getLogger(__name__)


class User(AbstractUser):
    """
    Custom User Model.

    Configure in `settings.py`:
        ```
        AUTH_USER_MODEL = "webapp.User"
        ```

    Model extends AbstractUser to store information
    specific to an APC User. Core function is to return
    information about verified status and social account
    details.
    """

    @property
    def is_verified(self) -> bool:
        """
        Return Verification Status.

        Return True if any of the registered email
        addresses have been verified. Filter all `EmailAddress`es
        for this user `self`.
        """
        queryset = EmailAddress.objects.filter(
            user=self,
            verified=True,
            primary=True
        )
        return queryset.count() > 0

    public = models.BooleanField(default=False)
    consent = models.BooleanField(default=False)
    # dob = models.DateField(blank=True, null=True)


class Profile(models.Model):
    """
    Also: ActivityPub Profile
    """
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(null=True)
    follows = models.ManyToManyField(
        "self",
        related_name="followed_by",
        symmetrical=False,
        blank=True
        )

    public = models.BooleanField(default=False)
    consent = models.BooleanField(default=False)
    dob = models.DateField(blank=True, null=True)
    gravatar = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    public_key_pem = models.TextField(blank=True)
    private_key_pem = models.TextField(blank=True)

    ap_id = models.CharField(max_length=255, blank=True)

    USER_ICONS = [
        ("0s", "0-square"),
    ]
    icon = models.CharField(
        max_length=2,
        choices=USER_ICONS,
        default="0s"
    )

    # Other Profiles # Consider
    mastodon = models.URLField(blank=True)

    img = models.ImageField(
        upload_to="mediafiles/user/",
        default="//storage.cloud.google.com/media.pramari.de/user/default.png"
    )

    @property
    def imgurl(self):
        """
        # import code for encoding urls and generating md5 hashes

        .. todo::
            make this work
        """
        import hashlib
        import urllib.parse

        # Set your variables here
        if self.user.is_verified:
            email = EmailAddress.objects.get(
                user=self.user,
                verified=True,
                primary=True
            )

        default = "https://www.example.com/default.jpg"
        size = 40

        # construct the url
        gravatar_url = "https://www.gravatar.com/avatar/" + \
            hashlib.md5(
                str(email).lower().encode('utf-8')
            ).hexdigest() + "?"
        gravatar_url += urllib.parse.urlencode({'d': default, 's': str(size)})
        return gravatar_url

    def __str__(self):
        return self.user.username  # pylint: disable=E1101

    def save(self, *args, **kwargs):
        from django.template.defaultfilters import slugify
        self.slug = slugify(self.user.username)
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def generate_jsonld(self):
        return {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1"
            ],
            "id": f"https://pramari.de{self.get_absolute_url}",
            "type": "Person",
            "name": self.user.username,
            "preferredUsername": self.user.username,
            "summary": self.bio,
            "inbox": f"https://pramari.de{self.get_inbox_url()}",
            "outbox": f"https://pramari.de{self.get_outbox_url()}",
            "followers": f"https://pramari.de{self.get_followers_url()}",
            "following": f"https://pramari.de{self.get_following_url()}",
            "publicKey": self.get_public_key(),
            "image": {
                "type": "Image",
                "mediaType": "image/jpeg",
                "url": self.imgurl
            },
            "icon": {
                "type": "Image",
                "mediaType": "image/png",
                "url": self.icon
            }
        }

    @property
    def get_absolute_url(self):
        return reverse(
            'profile-detail',
            args=[str(self.slug)]
        )

    def get_profile_url(self):
        return self.get_absolute_url

    def get_inbox_url(self):
        return reverse(
            'profile-inbox',
            args=[self.slug],
        )

    def get_outbox_url(self):
        return reverse(
            'profile-outbox',
            args=[self.slug],
        )

    def get_followers_url(self):
        return reverse(
            'profile-followers',
            args=[self.slug],
        )

    def get_following_url(self):
        return reverse(
            'profile-following',
            args=[self.slug],
        )

    def get_public_key(self):
        public_key_data = {
            "id": f"{self.get_profile_url()}#main-key",
            "owner": self.get_absolute_url,
            "publicKeyPem": self.public_key_pem
        }
        return public_key_data

"""
# can this be removed?
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # create a new profile instance for every user created.
    # leverage `Django Signals` for this purpose.
    
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

@receiver(pre_save, sender=Profile)
def save_profile(sender, instance, **kwargs):
    instance.ap_id = "https://pramari.de" + instance.get_absolute_url
"""

"""
class Attachment(models.Model):
    media_type = models.CharField(max_length=255)
    url = models.URLField()
    name = models.CharField(max_length=255, blank=True)
    # Add more fields as defined in the standard
"""

"""
class Object(models.Model):
    OBJECT_TYPES = (
        ('Article', 'Article'),
        ('Note', 'Note'),
        ('Image', 'Image'),
        ('Video', 'Video'),
        ('Audio', 'Audio'),
        # Add more object types as defined in the standard
    )

    object_type = models.CharField(max_length=255, choices=OBJECT_TYPES)
    content = models.TextField(blank=True)
    url = models.URLField(blank=True)
    attributed_to = models.ForeignKey(User, on_delete=models.CASCADE)
    published = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    in_reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    attachment = models.ManyToManyField('Attachment', blank=True)

    def __str__(self):
        return f"{self.object_type} ({self.pk})"
"""

"""
class Activity(models.Model):
    ACTIVITY_TYPES = (
        ('Accept', 'Accept'),
        ('Add', 'Add'),
        ('Announce', 'Announce'),
        ('Arrive', 'Arrive'),
        ('Block', 'Block'),
        ('Create', 'Create'),
        ('Delete', 'Delete'),
        ('Dislike', 'Dislike'),
        ('Flag', 'Flag'),
        ('Follow', 'Follow'),
        ('Ignore', 'Ignore'),
        ('Invite', 'Invite'),
        ('Join', 'Join'),
        ('Leave', 'Leave'),
        ('Like', 'Like'),
        ('Listen', 'Listen'),
        ('Move', 'Move'),
        ('Offer', 'Offer'),
        ('Question', 'Question'),
        ('Read', 'Read'),
        ('Reject', 'Reject'),
        ('Remove', 'Remove'),
        ('TentativeReject', 'TentativeReject'),
        ('TentativeAccept', 'TentativeAccept'),
        ('Travel', 'Travel'),
        ('Undo', 'Undo'),
        ('Update', 'Update'),
        ('View', 'View'),
        # Add more activity types as defined in the standard
    )
    # actor = models.URLField()
    actor = models.CharField(max_length=255)
    verb = models.CharField(max_length=255, choices=ACTIVITY_TYPES)
    object = models.JSONField()
    published = models.DateTimeField(auto_now_add=True)
    target = models.URLField(null=True, blank=True)

    # Additional fields as per your requirements

    def __str__(self):
        return f"{self.actor} {self.verb} {self.object}"
"""
 

"""
class InboxObject(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    actor = models.ForeignKey("Actor", on_delete=models.CASCADE)
    server = models.CharField(max_length=255)

    is_hidden_from_stream = models.BooleanField(default=False)

    ap_actor_id = models.CharField(max_length=255)
    ap_type = models.CharField(max_length=255)
    ap_id = models.CharField(max_length=255, unique=True)
    ap_context = models.CharField(max_length=255, null=True)
    ap_published_at = models.DateTimeField()
    ap_object = models.JSONField()

    activity_object_ap_id = models.CharField(max_length=255, null=True)

    visibility = models.CharField(max_length=255)
    conversation = models.CharField(max_length=255, null=True)

    has_local_mention = models.BooleanField(default=False)

    relates_to_inbox_object = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        related_name="related_inbox_objects"
    )
    relates_to_outbox_object = models.ForeignKey(
        "OutboxObject",
        on_delete=models.CASCADE,
        null=True,
        related_name="related_inbox_objects"
    )

    undone_by_inbox_object = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        related_name="undone_inbox_objects"
    )

    liked_via_outbox_object_ap_id = models.CharField(max_length=255, null=True)
    announced_via_outbox_object_ap_id = models.CharField(max_length=255, null=True)
    voted_for_answers = models.JSONField(null=True)

    is_bookmarked = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)
    is_transient = models.BooleanField(default=False)

    replies_count = models.IntegerField(default=0)

    og_meta = models.JSONField(null=True)

    @property
    def relates_to_anybox_object(self):
        if self.relates_to_inbox_object_id:
            return self.relates_to_inbox_object
        elif self.relates_to_outbox_object_id:
            return self.relates_to_outbox_object
        else:
            return None

    @property
    def is_from_db(self):
        return True

    @property
    def is_from_inbox(self):
        return True
"""
