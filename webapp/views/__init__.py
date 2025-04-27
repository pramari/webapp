#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 et

__name__ = "webapp.views"
__author__ = "Andreas Neumeier"

from .profile import (
    StatusView,
    AccountView,
    ProfileView,
    ProfileDetailView,
    SearchView,
)

from .signature import SignatureView

__all__ = [
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
