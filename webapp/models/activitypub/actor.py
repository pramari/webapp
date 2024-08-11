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
from webapp.validators import validate_iri
from functools import cached_property
from webapp.exceptions import RemoteActorError
from django.contrib.sites.models import Site
import uuid

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
        actor = Actor.objects.get(id='https://example.com/actor')

    The `Actor` object will provide required and some optional properties:

    .. testcode::

        actor.inbox

    This will produce the full url for the `inbox` of the actor:

    .. testoutput::

        'https://example.com/actor/inbox'

    The `Actor` object will provide required and some optional properties:

    .. testcode::
        actor.follows.all()
        actor.followed_by.all()

    Will return the `actors` that are `followed` by this `actor` and the
    `actors` that are `following` this `actor`:

    .. testoutput::
        <QuerySet [<Actor: https://23.social/users/andreasofthings>, <Actor: https://23.social/users/christianrickert>]>
        <QuerySet [<Actor: https://23.social/users/andreasofthings>]>
    """

    profile = models.ForeignKey(
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
        """
        if not self.remote:
            return f"{self.id}#main-key"
        raise RemoteActorError("Remote actors do not have a key-id.")

    @property
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
            return f"{base}%s" % reverse(
                "actor-inbox",
                args=[self.profile.slug],
            )
        raise RemoteActorError("Remote actors do not have a local inbox.")

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
        return reverse(
            "actor-followers",
            args=[self.profile.slug],
        )

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


"""
class Fllwng(models.Model):
    # id = models.CharField(max_length=255, primary_key=True, unique=True, blank=False, validators=[validate_iri])
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, related_name="actor")
    object = models.ForeignKey(Actor, on_delete=models.CASCADE, related_name="object")
    id = models.CharField(
        max_length=255,
        primary_key=True,
        unique=True,
        blank=False,
        validators=[validate_iri],
    )
    accepted = models.URLField(blank=True, null=True, validators=[validate_iri])
"""
