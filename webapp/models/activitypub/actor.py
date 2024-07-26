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
    Activity Streams 2.0 - Actor



    .. type:: Actor

    .. seealso::
        `Actor Objects <https://www.w3.org/TR/activitypub/#actor-objects>`_

    .. py:class:: webapp.models.Actor

        `:py:class:Actor` objects **MUST** have, in addition to the properties
        mandated by `Object Identifiers <https://www.w3.org/TR/activitypub/#obj-id>`_,  # noqa: E501
        the following properties:

    .. py:property:: `self.inbox`

        :type: URL
        :classmethod:

        return a link to an `OrderedCollection`: An `Inbox` is a
        `Collection` to which `Items` are added, typically by the `owner` of
        the `Inbox`. The `inbox` property is REQUIRED for `Actor` objects.

    .. py:property:: outbox

        :type: URL
        :classmethod:

        return a link to an `OrderedCollection`: An `Outbox` is a
        `Collection` to which `Items` are added, typically by the `owner`
        of the `Outbox`. The `outbox` property is REQUIRED for `Actor` objects.

    .. py:property:: following

        :type: URL
        :classmethod:

        return a link to an `OrderedCollection`: A collection of
        `actors` that this `actor` is `following`. The `following` property
        is OPTIONAL for `Actor` objects.

    - `:py:attr:followers` (Link to an `OrderedCollection`): A collection of `actors`
    that follow this `actor`. The `followers` property is OPTIONAL for `Actor`
    objects.

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

    follows = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
    )

    class Meta:
        verbose_name = _("Actor (Activity Streams 2.0)")
        verbose_name_plural = _("Actors (Activity Streams 2.0)")
        unique_together = ("id", "type", "profile")

    def __str__(self):
        """
        Return the string representation of the object.
        """
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
    def remote(self):
        """
        If this does not belong to a profile, it is remote.
        """
        return self.profile_set.count() == 0

    @property
    def inbox(self):
        """
        :py:attr:inbox returns a link to an `OrderedCollection`

        Return the URL of the inbox.

        :: return: URL
        :: rtype: str

        .. seealso::
            :py:class:`webapp.views.inbox.InboxView`

        """
        return reverse(
            "actor-inbox",
            args=[self.profile.slug],
        )

    @property
    def outbox(self):
        """
        :py:attr:outbox returns a link to an `OrderedCollection`

        Return the URL of the outbox.

        :: return: URL
        :: rtype: str

        .. seealso::
            :py:class:`webapp.views.outbox.OutboxView`
        """
        return reverse(
            "actor-outbox",
            args=[self.profile.slug],
        )

    @property
    def followers(self):
        """
        Return the URL of the followers.

        .. seealso::
            :py:class:`webapp.views.followers.FollowersView`
        """
        return reverse(
            "actor-followers",
            args=[self.profile.slug],
        )

    @property
    def following(self):
        """
            :py:attr:following returns a link to an `OrderedCollection`, a
            collection of `actors` that this `actor` is `following`.

        .. seealso::
            :py:class:FollowingView

        :: return: URL
        :: rtype: str
        """
        return reverse(
            "actor-following",
            args=[self.profile.slug],
        )

    @property
    def liked(self):
        """
        Following the definition of the `Activity Streams 2.0` specification,
        the `liked` property returns a link to a collection of `Objects` tha
        this `actor` has `liked`.

        Return the URL to the likes-collection.

        :: return: URL
        :: rtype: str

        """
        return reverse(
            "actor-likes",
            args=[self.profile.slug],
        )

    @property
    def key_id(self) -> str:
        """
        The :py:class:Actor main key-id.
        """
        return f"{self.id}#main-key"
