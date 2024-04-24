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

from webapp.views import (
    NodeInfoView,
    VersionView,
    WebFingerView,
    ActorView,
    InboxView,
    OutboxView,
    FollowView,
    FollowersView,
    FollowingView,
    NoteView,
    ActionView,
)

logger = logging.getLogger(__name__)

urlpatterns = [
    # /.well-known/nodeinfo
    path(".well-known/nodeinfo", NodeInfoView.as_view(), name="nodeinfo"),
    path("api/v1/version", VersionView.as_view(), name="version"),
    path(".well-known/webfinger", WebFingerView.as_view(), name="webfinger"),
    # path('activity/', include('actstream.urls')),
    # path('inbox/', InboxView.as_view(), name='profile-inbox'),
    # path('outbox/', OutboxView.as_view(), name='profile-outbox'),
    path(
        r"accounts/<slug:slug>/inbox",
        InboxView.as_view(),
        name="profile-inbox",  # noqa: E501
    ),
    path(
        r"accounts/<slug:slug>/outbox",
        OutboxView.as_view(),
        name="profile-outbox",  # noqa: E501
    ),
    path(r"follow/", FollowView.as_view(), name="profile-follow"),
    # path(
    #    'activity/<str:activity_id>/',
    #    ActivityView.as_view(),
    #    name='activity-detail'
    # ),
    path(
        r"accounts/<slug:slug>/actor/",
        ActorView.as_view(),
        name="actor-view",  # noqa: E501
    ),
    path(
        r"accounts/<slug:slug>/followers",
        FollowersView.as_view(),
        name="profile-followers",
    ),
    path(
        r"accounts/<slug:slug>/following",
        FollowingView.as_view(),
        name="profile-following",
    ),
]

urlpatterns += [
    path(r"note/<uuid:pk>", NoteView.as_view(), name="note-detail"),
    path(r"action/<uuid:pk>", ActionView.as_view(), name="action-detail"),
]
