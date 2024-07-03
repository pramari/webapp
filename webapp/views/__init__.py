#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 et

__name__ = "webapp.views"
__author__ = "Andreas Neumeier"

from .web import (
    HomeView,
    StatusView,
    AccountView,
    ProfileView,
    ProfileDetailView,
    SearchView,
)

from .webfinger import WebFingerView
from .actor import ActorView
from .inbox import InboxView
from .outbox import OutboxView
from .followers import FollowersView
from .following import FollowingView

from .activitypub import (
    NodeInfoView,
    VersionView,
    # FollowView,
)

from .activity import (
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
    "NoteView",
    "ActionView",
]
