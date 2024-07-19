#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4
# pylint: disable=invalid-name

"""
Activitypub models for `Angry Planet Cloud`.

"""
import logging
from django.db import models
from webapp.models.profile import Profile
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

# from django.contrib.sites.models import Site

logger = logging.getLogger(__name__)


def get_actor_types():
    """
    Activity Streams 2.0 Abstraction Layer for Activity Types
    """
    # from webapp.schema import ACTOR_TYPES
    ACTOR_TYPES = {
        "Application": _("Application"),
        "Group": _("Group"),
        "Organization": _("Organization"),
        "Person": _("Person"),
        "Service": _("Service"),
    }
    return ACTOR_TYPES


class Actor(models.Model):
    """
    Activity Streams 2.0

    Actor
    """

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, null=True
    )

    id = models.CharField(
        max_length=255, primary_key=True, unique=True, blank=False
    )  # noqa: E501

    type = models.CharField(
        max_length=255, default="Person", choices=get_actor_types
    )  # noqa: E501

    # slug = profile.slug
    # preferredUsername = profie.preferredUsername

    following = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False, blank=True
    )

    class Meta:
        verbose_name = _("Actor (Activity Streams 2.0)")
        verbose_name_plural = _("Actors (Activity Streams 2.0)")
        unique_together = ("id", "type", "profile")

    @property
    def remote(self):
        """
        If this does not belong to a profile, it is remote.
        """
        return self.profile_set.count() == 0

    def __str__(self):
        return self.id

    @property
    def actorID(self):
        """
        Return the URL of the actor.
        Activity Streams 2.0

        .. todo::
            This is not the same as `get_absolute_url`, but the actor ID,
            that is stored in self.ap_id
            Currently only the `actor-view` does use this.
        """

        # return self.ap_id
        view = reverse("actor-view", args=[str(self.profile.user)])
        return f"{view}"

    @property
    def inbox(self):
        """
        Return the URL of the inbox.

        """
        return reverse(
            "actor-inbox",
            args=[self.profile.slug],
        )

    @property
    def outbox(self):
        """
        Return the URL of the outbox.
        """
        return reverse(
            "actor-outbox",
            args=[self.profile.slug],
        )

    @property
    def followers_url(self):
        """
        Return the URL of the followers.
        """
        return reverse(
            "actor-followers",
            args=[self.profile.slug],
        )

    @property
    def following_url(self):
        """
        Return the URL of the following.
        """
        return reverse(
            "actor-following",
            args=[self.profile.slug],
        )

    @property
    def likes_url(self):
        """
        Return the URL for likes.
        """
        return reverse(
            "actor-likes",
            args=[self.profile.slug],
        )

    @property
    def get_key_id(self) -> str:
        """
        Return the key id.
        """
        return f"{self.id}#main-key"
