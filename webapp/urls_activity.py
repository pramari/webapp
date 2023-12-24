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

from .ActivityView import (
    #    WebFingerView,
    #    ActorView,
    #    InboxView,
    #    OutboxView,
    #    FollowView,
    FollowersView,
    FollowingView,
)

logger = logging.getLogger(__name__)

urlpatterns = [
    # path('.well-known/webfinger', WebFingerView.as_view(), name='webfinger'),
    # path('activity/', include('actstream.urls')),
    # path('inbox/', InboxView.as_view(), name='profile-inbox'),
    # path(
    #     r'accounts/<slug:slug>/inbox',
    #     InboxView.as_view(),
    #     name='profile-inbox'
    # ),
    # path('outbox/', OutboxView.as_view(), name='profile-outbox'),
    # path(
    #     r'accounts/<slug:slug>/outbox',
    #     OutboxView.as_view(),
    #     name='profile-outbox'
    # ),
    # path('follow/', FollowView.as_view(), name='profile-follow'),
    # path(
    #    'activity/<str:activity_id>/',
    #    ActivityView.as_view(),
    #    name='activity-detail'
    # ),
    # path(
    #    r'accounts/<slug:slug>/actor',
    #    ActorView.as_view(),
    #    name='activity-view'
    # ),
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
