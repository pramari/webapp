#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 et

__name__ = "webapp.views"
__author__ = "Andreas Neumeier"

from .profile import (
    HomeView,
    StatusView,
    AccountView,
    ProfileView,
    ProfileDetailView,
    SearchView,
)

from .activitypub.webfinger import WebFingerView
from .activitypub.actor import ActorView
from .activitypub.inbox import InboxView
from .activitypub.outbox import OutboxView
from .activitypub.followers import FollowersView
from .activitypub.following import FollowingView


from .activitypub import (
    NodeInfoView,
    VersionView,
    # FollowView,
)

from .activitypub.activity import (
    NoteView,
    ActionView,
)

from .signature import SignatureView

__all__ = [
    "HomeView",
    "StatusView",
    "AccountView",
    "ProfileView",
    "ProfileDetailView",
    "SearchView",
]

__all__ += [
    "NodeInfoView",
    "VersionView",
    "WebFingerView",
    "ActorView",
    "InboxView",
    "OutboxView",
    "FollowView",
    "FollowersView",
    "FollowingView",
    "SignatureView",
]

__all__ += [
    "LikeCreateView",
    "LikeDeleteView",
    "LikeDetailView",
    "LikeListView",
]

__all__ += [
    "NoteView",
    "ActionView",
]
