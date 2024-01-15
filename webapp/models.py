#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
Models for `Angry Planet Cloud`.

At the time, this file exists for `Django` only, however, this
may be the right home for an `Usermodel` in the future.
"""

from django.contrib.auth.models import AbstractUser  # type: ignore
from django.db.models.signals import pre_save, post_save  # type: ignore
from django.dispatch import receiver  # type: ignore
from django.db import models  # type: ignore
from django.urls import reverse

from allauth.account.models import EmailAddress  # type: ignore

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
        queryset = EmailAddress.objects.filter(user=self, verified=True, primary=True)
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
        try:
            # from allauth.socialaccount.models import SocialToken, SocialApp,
            from allauth.socialaccount.models import SocialAccount
        except ImportError:
            logger.error("Cannot import SocialToken")
        try:
            accounts = SocialAccount.objects.filter(user=self.request.user)
            """
            accessToken = SocialToken.objects.filter(  # pylint: disable=no-member
                account__user=self  # provider
            )
            """
        except SocialAccount.DoesNotExist:
            accounts = [
                "none",
            ]
        logger.error(type(accounts))
        logger.error(accounts)
        return accounts

    @property
    def get_absolute_url(self):
        return reverse(
            "user-detail",
        )


class Profile(models.Model):
    """
    Also: ActivityPub Profile
    """

    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(null=True)
    follows = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
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
    icon = models.CharField(max_length=2, choices=USER_ICONS, default="0s")

    # Other Profiles # Consider
    mastodon = models.URLField(blank=True)

    img = models.ImageField(
        upload_to="mediafiles/user/",
        default="//storage.cloud.google.com/media.pramari.de/user/default.png",
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
                user=self.user, verified=True, primary=True
            )

        default = "https://www.example.com/default.jpg"
        size = 40

        # construct the url
        gravatar_url = (
            "https://www.gravatar.com/avatar/"
            + hashlib.md5(str(email).lower().encode("utf-8")).hexdigest()
            + "?"
        )
        gravatar_url += urllib.parse.urlencode({"d": default, "s": str(size)})
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
                "https://w3id.org/security/v1",
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
            "image": {"type": "Image", "mediaType": "image/jpeg", "url": self.imgurl},
            "icon": {"type": "Image", "mediaType": "image/png", "url": self.icon},
        }

    @property
    def get_absolute_url(self):
        return reverse("profile-detail", args=[str(self.slug)])

    def get_profile_url(self):
        return self.get_absolute_url

    def get_inbox_url(self):
        return reverse(
            "profile-inbox",
            args=[self.slug],
        )

    def get_outbox_url(self):
        return reverse(
            "profile-outbox",
            args=[self.slug],
        )

    def get_followers_url(self):
        return reverse(
            "profile-followers",
            args=[self.slug],
        )

    def get_following_url(self):
        return reverse(
            "profile-following",
            args=[self.slug],
        )

    def get_public_key(self):
        public_key_data = {
            "id": f"{self.get_profile_url()}#main-key",
            "owner": self.get_absolute_url,
            "publicKeyPem": self.public_key_pem,
        }
        return public_key_data
