#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4
# pylint: disable=invalid-name

"""
urls_activity.py.

urls necessary to make all social views work.

"""

import logging

from django.urls import path
from django.urls import include

from webapp.activitypub.views import (
    WebFingerView,
    NodeInfoView,
    VersionView,
    TimelineView,
    StreamingView,
)

from webapp.activitypub.views import (
    ActorView,
    InboxView,
    OutboxView,
    FollowersView,
    FollowingView,
    LikedView,
)

from webapp.activitypub.views.activity import (
    NoteView,
    ActionView,
)


logger = logging.getLogger(__name__)

urlpatterns = [
    # /.well-known/nodeinfo
    path(".well-known/nodeinfo", NodeInfoView.as_view(), name="nodeinfo"),
    path(".well-known/webfinger", WebFingerView.as_view(), name="webfinger"),
    path("api/v1/version", VersionView.as_view(), name="version"),
    path("api/v1/timeline", TimelineView.as_view(), name="timeline"),
    path("api/v1/streaming", StreamingView.as_view(), name="streaming"),
    path(
        r"@<slug:slug>",
        ActorView.as_view(),
        name="actor-view",  # noqa: E501
    ),
    path(
        r"@<slug:slug>/inbox",
        InboxView.as_view(),
        name="actor-inbox",  # noqa: E501
    ),
    path(
        r"accounts/<slug:slug>/outbox",
        OutboxView.as_view(),
        name="actor-outbox",  # noqa: E501
    ),
    # path(r"follow/", FollowView.as_view(), name="profile-follow"),
    path(
        r"accounts/<slug:slug>/followers",
        FollowersView.as_view(),
        name="actor-followers",
    ),
    path(
        r"accounts/<slug:slug>/following",
        FollowingView.as_view(),
        name="actor-following",
    ),
    path(
        r"accounts/<slug:slug>/liked",
        LikedView.as_view(),
        name="actor-liked",
    ),
]

urlpatterns += [
    path(r"note/<uuid:pk>", NoteView.as_view(), name="note-detail"),
    path(r"action/<uuid:pk>", ActionView.as_view(), name="action_detail"),
]

urlpatterns += [
    path(r"web/", include("webapp.activitypub.urls.web")),
]
