#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4
# pylint: disable=invalid-name

"""
Activitypub models for `Angry Planet Cloud`.

"""
import logging
import uuid
from functools import cached_property

from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from webapp.activitypub.validators import validate_iri
from webapp.exceptions import RemoteActorError
from webapp.models.profile import Profile

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

    :py:class:webapp.models.activitypub:Actor objects **MUST** have, in
    addition to the properties mandated by `Object Identifiers <https://www.w3.org/TR/activitypub/#obj-id>`_,  # noqa: E501
    the following properties:


        - `actorID` -  A unique `URL` for the `Actor`. The `id` property is *REQUIRED*
        for `Actor` objects.

        - `inbox` - A link to an `OrderedCollection` of `Activities` that this
        `Actor` has received, typically from clients. The `inbox` property is
        *REQUIRED* for `Actor` objects.

        - `outbox` - A link to an `OrderedCollection` of `Activities` that this
        `Actor` has published, such as `Posts`, `Comments`, etc. The `outbox`
        property is *REQUIRED* for `Actor` objects.

        - `followers` - A link to an `OrderedCollection` of `actors` that are
        `following` this `actor`. The `followers` property is *OPTIONAL* for
        `Actor` objects.

        - `following` - A link to an `OrderedCollection` of `actors` that this
        `actor` is `following`. The `following` property is *OPTIONAL* for
        `Actor` objects.

        - `liked` - A link to an `OrderedCollection` of `Objects` that this
        `actor` has `liked`. The `liked` property is *OPTIONAL* for `Actor`
        objects.

        - `follows` - a django `ManyToManyField` relationship to `self` that
        stores any `actors` that this `actor` is `follows`.

        - `followed_by` - a django `ManyToManyField` relationship to `self` that
        stores any `actors` that are `following` this `actor`.


    .. seealso::
        The definition of W3C ActivityPub `Actor Objects <https://www.w3.org/TR/activitypub/#actor-objects>`_

    .. testsetup::

        from webapp.models.actor import Actor

    The model persists the `Actor` object in the database. The `Actor` object
    provides all the necessary properties to interact with the
    `Activity Streams 2.0` specification. Just like with regualar Django
    objects, you can create, update, delete and query `Actor` objects:

    .. doctest::

        Actor.objects.create(id='https://example.com/actor')
        Actor.objects.create(id='https://example.com/other')
        actor = Actor.objects.get(id='https://example.com/actor')
        other = Actor.objects.get(id='https://example.com/other')

    The `Actor` object will provide required and some optional properties:

    .. testcode::

        actor.id

    This will produce the full url for the `inbox` of the actor:

    .. testoutput::

        'https://example.com/actor'

    The `Actor` object will provide required and some optional properties:

    .. testcode::
        actor.follows.add(other)
        actor.follows.all()

    This will add the `other` actor to the `follows` of the `actor`:

    .. testoutput::

        <QuerySet [<Actor: https://example.com/other>]>
    """

    # profile = models.ForeignKey(
    #    Profile, on_delete=models.CASCADE, blank=True, null=True
    # )

    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, blank=True, null=True
    )

    id = models.CharField(
        max_length=255,
        primary_key=True,
        unique=True,
        blank=False,
        validators=[validate_iri],
    )  # noqa: E501

    type = models.CharField(
        max_length=255, default="Person", choices=get_actor_types
    )  # noqa: E501

    # slug = profile.slug
    # preferredUsername = profie.preferredUsername

    follows = models.ManyToManyField(
        "self",
        related_name="followed_by",
        symmetrical=False,
        blank=True,
        through="Follow",
    )

    # flw = models.ManyToManyField(  # this is to prep/test migration of the above.
    #     "self", related_name="flwng", symmetrical=False, blank=True, through="Fllwng"
    # )

    class Meta:
        verbose_name = _("Actor (Activity Streams 2.0)")
        verbose_name_plural = _("Actors (Activity Streams 2.0)")
        unique_together = ("id", "type", "profile")

    def __str__(self):
        """
        Return the string representation of the object.
        """
        return str(self.id)

    @cached_property
    def actorID(self):
        """
        Return the URL of the actor.
        Activity Streams 2.0

        .. todo::
            This is not the same as `get_absolute_url`, but the actor ID,
            that is stored in self.ap_id
            Currently only the `actor-view` does use this.

        .. deprecated:: 0.1.0
            see :py:attr:`id` instead.
        """

        # return self.ap_id
        logger.error("The actorID property is deprecated. Use id instead.")
        view = reverse("actor-view", args=[str(self.profile.user)])
        return f"{view}"

    @cached_property
    def remote(self):
        """
        If this does not belong to a profile, it is remote.
        """
        return self.profile is None

    @property
    def publicKey(self) -> str:
        """
        The :py:class:Actor main public-key.

        .. todo::
            This currently lives in the parent profile.
            It should be moved to the Actor object.
        """
        if not self.remote:
            return f"{self.profile.public_key_pem}"
        raise RemoteActorError("Remote actors do not have a public key.")

    @property
    def keyID(self) -> str:
        """
        The :py:class:Actor main key-id.

        .. todo::
            Implement a mechanism to keep other keys
            than the main key; and to rotate keys.
        """
        if not self.remote:
            return f"{self.id}#main-key"
        raise RemoteActorError("Remote actors do not have a key-id.")

    @cached_property
    def inbox(self):
        """
        :py:attr:inbox returns a link to an `OrderedCollection`

        Return the URL of the `inbox`, that contains an `OrderedCollection`.
        An `Inbox` is a `Collection` to which `Items` are added, typically by
        the `owner` of the `Inbox`. The `inbox` property is *REQUIRED* for
        `Actor` objects.

        :: return: URL
        :: rtype: str

        .. seealso::
            :py:class:`webapp.views.inbox.InboxView`

        """
        if not self.remote:
            base = f"https://{Site.objects.get_current().domain}"
            return f"{base}" + reverse(
                "actor-inbox",
                args=[self.profile.slug],
            )
        raise RemoteActorError("Remote actors do not have a local inbox.")

    @cached_property
    def outbox(self):
        """
        :py:attr:outbox returns a link to an `OrderedCollection`

        Return the URL of the outbox.

        :: return: URL
        :: rtype: str

        .. seealso::
            :py:class:`webapp.views.outbox.OutboxView`
        """
        if not self.remote:
            base = f"https://{Site.objects.get_current().domain}"
            return f"{base}%s" % reverse(
                "actor-outbox",
                args=[self.profile.slug],
            )
        raise RemoteActorError("Remote actors do not have a local outbox.")

    @property
    def followers(self):
        """
        `followers` will return the URL to an `OrderedCollection`, a
        collection of `actors` that are `following` this `actor`.

        :return: URL

        .. seealso::
            The view to serve this `OrderedCollection` is served by
            :py:class:`webapp.views.followers.FollowersView`

        .. seealso:: Following the `Activity Streams 2.0` specification for
            `followers <https://www.w3.org/TR/activitypub/#actor-objects>`_,
            the `followers` property is OPTIONAL.


        """
        if not self.remote:
            base = f"https://{Site.objects.get_current().domain}"
            return f"{base}%s" % reverse(
                "actor-followers",
                args=[self.profile.slug],
            )
        raise RemoteActorError("Remote actors do not have a local follower.")

    @property
    def following(self):
        """
        `following` returns a link to an `OrderedCollection`, a
        collection of `actors` that this `actor` is `following`.

        :return: URL
        :rtype: str

        .. seealso::
            The view to serve this `OrderedCollection` is served by
            :py:class:`webapp.views.following.FollowingView`

        """
        if not self.remote:
            base = f"https://{Site.objects.get_current().domain}"
            return f"{base}%s" % reverse(
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
        if not self.remote:
            base = f"https://{Site.objects.get_current().domain}"
            return f"{base}%s" % reverse(
                "actor-liked",
                args=[self.profile.slug],
            )


class Follow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, related_name="actor")
    object = models.ForeignKey(Actor, on_delete=models.CASCADE, related_name="object")
    accepted = models.URLField(blank=True, null=True, validators=[validate_iri])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def getID(self):
        from django.contrib.sites.models import Site

        base = f"https://{Site.objects.get_current().domain}"
        return f"{base}/{self.id}"

    def __str__(self):
        return f"{self.actor} follows {self.object}"
