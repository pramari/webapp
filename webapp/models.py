#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
Models for `Angry Planet Cloud`.

At the time, this file exists for `Django` only, however, this
may be the right home for an `Usermodel` in the future.
"""

import hashlib
import urllib.parse
import logging
import uuid

from django.contrib.auth.models import AbstractUser  # type: ignore
from django.db import models  # type: ignore
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from allauth.account.models import EmailAddress  # type: ignore

from .managers import ActionManager

logger = logging.getLogger(__name__)

try:
    # from allauth.socialaccount.models import SocialToken, SocialApp,
    from allauth.socialaccount.models import SocialAccount  # type
except ImportError:
    logger.error("Cannot import SocialToken")


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
        queryset = EmailAddress.objects.filter(  # noqa: E501
            user=self, verified=True, primary=True
        )
        return queryset.count() > 0

    public = models.BooleanField(default=False)
    consent = models.BooleanField(default=False)
    # dob = models.DateField(blank=True, null=True)

    @property
    def services(self) -> list[str]:
        """
        List all services a user has associated.

        returns:
            List of strings.
        """
        accounts = []
        try:
            accounts = SocialAccount.objects.filter(
                user=self.request.user
            )  # pylint: disable=E1101,E501
        except SocialAccount.DoesNotExist:
            accounts = [
                "none",
            ]
        logger.error(type(accounts))
        logger.error(accounts)
        return ["A"]  # accounts

    @property
    def get_absolute_url(self):
        """
        Default Django Method/Best Practice
        """
        return reverse(
            "user-detail",
        )


class Profile(models.Model):
    """
    Also: ActivityPub Profile
    """

    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(null=True, help_text=_("Slug"))
    follows = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
    )

    public = models.BooleanField(
        default=False, help_text=_("Make Profile Profile public?")
    )
    consent = models.BooleanField(
        default=False, help_text=_("Consent to store and use data.")
    )
    dob = models.DateField(
        blank=True, null=True, help_text=_("Date of Birth (DOB)")
    )  # noqa: E501
    gravatar = models.BooleanField(
        default=True, help_text=_("Use Gravatar profile image.")
    )
    bio = models.TextField(blank=True, help_text=_("Short Bio"))

    ap_id = models.CharField(
        max_length=255, blank=True, help_text=_("ActivityPub ID")
    )  # noqa: E501
    key_id = models.CharField(
        max_length=255, blank=True, help_text=_("Key ID")
    )  # noqa: E501
    public_key_pem = models.TextField(blank=True, help_text=_("Public Key"))
    private_key_pem = models.TextField(blank=True, help_text=_("Private Key"))

    USER_ICONS = [
        ("0s", "0-square"),
    ]
    icon = models.CharField(max_length=2, choices=USER_ICONS, default="0s")

    # Other Profiles # Consider
    mastodon = models.URLField(blank=True)

    img = models.ImageField(
        upload_to="mediafiles/user/",
        default="https://storage.cloud.google.com/media.pramari.de/user/default.png",  # noqa: E501
    )

    @property
    def imgurl(self):
        """
        Return the URL of the profile image.

        First, if the user is not verified, the user will not be allowed
        to have a custom gravatar. Instead, a default image will be used.

        Second, if the user is verified, the user will be allowed to have
        a custom avatar. The user can choose to use a gravatar or a custom
        image.

        .. todo::
            make this work
        """
        size = 80

        # Set your variables here
        if self.user.is_verified:  # noqa: no-member
            email = EmailAddress.objects.get(
                user=self.user, verified=True, primary=True
            )
        else:
            return "https://storage.cloud.google.com/media.pramari.de/user/default.png"  # noqa: E501

        # construct the url
        if self.gravatar is False:
            return staticfiles_storage.url(self.img)
        else:
            hashvalue = hashlib.md5(
                str(email).lower().encode("utf-8")
            ).hexdigest()  # noqa: E501
            size = urllib.parse.urlencode({"d": email, "s": str(size)})
            return f"https://www.gravatar.com/avatar/{hashvalue}?{size}"

    def __str__(self):
        """
        Default Python Method/Best Practice for String Representation
        """
        return self.user.username  # pylint: disable=E1101

    def save(self, *args, **kwargs):
        """
        Profile.save()

        Create a slug from the username if none is provided.
        """
        if not self.slug:
            self.slug = slugify(self.user.username)  # pylint: disable=E1101
        if not self.ap_id and self.user.is_verified:
            self.ap_id = f"https://pramari.de/@{self.slug}"
        if not self.key_id:
            self.key_id = f"{self.ap_id}#main-key"
        return super().save(*args, **kwargs)  # Call the "real" save() method.

    @property
    def get_absolute_url(self):
        """
        Default Django Method/Best Practice
        Returns the URL of the object-detail view.
        """
        return reverse("profile-detail", args=[str(self.slug)])

    @property
    def get_actor_url(self):
        """
        Return the URL of the actor.
        Activity Streams 2.0

        .. todo::
            This is not the same as `get_absolute_url`, but the actor ID,
            that is stored in self.ap_id
            Currently only the `actor-view` does use this.
        """
        return self.ap_id
        # return reverse("actor-view", args=[str(self.slug)])

    @property
    def get_inbox_url(self):
        """
        Return the URL of the inbox.

        """
        return reverse(
            "profile-inbox",
            args=[self.slug],
        )

    @property
    def get_outbox_url(self):
        """
        Return the URL of the outbox.
        """
        return reverse(
            "profile-outbox",
            args=[self.slug],
        )

    @property
    def get_followers_url(self):
        """
        Return the URL of the followers.
        """
        return reverse(
            "profile-followers",
            args=[self.slug],
        )

    @property
    def get_following_url(self):
        """
        Return the URL of the following.
        """
        return reverse(
            "profile-following",
            args=[self.slug],
        )

    @property
    def get_key_id(self) -> str:
        """
        Return the key id.
        """
        return f"{self.key_id}"

    def get_public_key(self, base: str) -> dict[str, str]:
        """
        Return the public key as JSON-LD.
        """
        actorid = f"{self.get_actor_url}"
        public_key_data = {
            "id": f"{self.get_key_id}",
            "owner": actorid,
            "publicKeyPem": self.public_key_pem,
        }
        return public_key_data

        #   @property
        #   def activities(self) -> list:
        """
        Return all activities of this profile.

        .. todo::
            Implement this.
        """

    #    return Action.objects.filter(actor=self)


class Action(models.Model):
    """
    Activity Streams 2.0

    Inp
    https://github.com/justquick/django-activity-stream/blob/main/actstream/models.get_profile_types
    """

    objects = ActionManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=now, db_index=True)
    public = models.BooleanField(default=True, db_index=True)

    actor_content_type = models.ForeignKey(
        ContentType,
        related_name="actor",
        on_delete=models.CASCADE,
        db_index=True,  # noqa: E501
    )
    actor_object_id = models.CharField(max_length=255, db_index=True)
    actor = GenericForeignKey("actor_content_type", "actor_object_id")

    verb = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    target_content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name="target",
        on_delete=models.CASCADE,
        db_index=True,
    )
    target_object_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )
    target = GenericForeignKey("target_content_type", "target_object_id")

    action_object_content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name="action_object",
        on_delete=models.CASCADE,
        db_index=True,
    )
    action_object_object_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )
    action_object = GenericForeignKey(
        "action_object_content_type", "action_object_object_id"
    )

    timestamp = models.DateTimeField(default=now, db_index=True)

    public = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ("-timestamp",)

    def __str__(self):
        details = {
            "actor": str(self.actor),
            "verb": self.verb,
            "target": str(self.target),
            "since": self.since(),
        }
        if self.target:
            if self.action_object:
                return _(
                    f"{details['actor']} {details['verb']} {details['action_object']} on {details['target']} {details['since']}s ago"  # noqa: E501
                )
            return _(
                f"{details['actor']} {details['verb']} {details['target']} {details['since']}s ago"  # noqa: E501
            )  # noqa: E501
        if self.action_object:
            return _(
                f"{self.actor} {self.verb} {self.action_object} {self.since}s ago"  # noqa: E501
            )  # noqa: E501
        return _(
            f"{self.actor} {self.verb}"
        )  # _(f"{self.actor} {self.verb} {self.since} ago")

    def since(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince

        return (
            timesince(self.timestamp, now)
            .encode("utf8")
            .replace(b"\xc2\xa0", b" ")
            .decode("utf8")
        )

    def get_absolute_url(self):
        return reverse("action_detail", args=[self.pk])


class Note(models.Model):
    """
    Activity Streams 2.0

    Note
    """

    class Meta:
        verbose_name = _("Note (Activity Streams 2.0)")
        verbose_name_plural = _("Notes (Activity Streams 2.0)")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    content = models.TextField()

    published = models.DateTimeField(default=now, db_index=True)
    updated = models.DateTimeField(default=now, db_index=True)

    public = models.BooleanField(default=True, db_index=True)
    sensitive = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse("note-detail", args=[self.id])
