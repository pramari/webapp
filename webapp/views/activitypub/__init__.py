"""
:py:module:`webapp.views.activitypub` -- ActivityPub API views

This module contains the views for the ActivityPub API.

The primary goal is to implement server-to-server communication, with
later plans to implement client-to-server communication.

The module contains acompanies views to use the ActivityPub API, 
such as NodeInfo and WebFinger.

The views are designed to be used with Django's class-based views.

W3C ActivityPub is a protocol for federated social networking 
based on the ActivityStreams 2.0 data format.

.. seealso::
    `W3C ActivityPub <https://www.w3.org/TR/activitypub/>`_
    `W3C ActivityStreams 2.0 <https://www.w3.org/TR/activitystreams-core/>`_
"""

from .nodeinfo import NodeInfoView, VersionView
from .webfinger import WebFingerView
from .actor import ActorView
from .inbox import InboxView
from .outbox import OutboxView
from .followers import FollowersView
from .following import FollowingView
from .liked import LikedView

__all__ = [
    "NodeInfoView",
    "VersionView",
    "WebFingerView",
    "ActorView",
    "InboxView",
    "OutboxView",
    "FollowersView",
    "FollowingView",
    "LikedView"
]
