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

from .activitypub import (
    NodeInfoView,
    VersionView,
    WebFingerView,
    ActorView,
    InboxView,
    OutboxView,
    FollowView,
    FollowersView,
    FollowingView,
)

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
]
