#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4
# pylint: disable=invalid-name

"""
urls.py.

Route traffic to code.
"""

import logging


from django.urls import path
from django.conf.urls import include
from django.views.decorators.cache import cache_page  # , never_cache

from webapp.views import (
    StatusView,
    HomeView,
    AccountView,
    ProfileView,
    ProfileDetailView,
    SearchView,
)

from webapp.urls.activitypub import urlpatterns as activitypub_urlpatterns
from webapp.urls.api import urlpatterns as api_urlpatterns


logger = logging.getLogger(__name__)


urlpatterns = [
    path(r"", HomeView.as_view(), name="home"),
    path(
        r"status/", cache_page(60)(StatusView.as_view()), name="status"
    ),  # Project Status, Could be a template view
    path(r"search/", SearchView.as_view(), name="search_result"),
]

urlpatterns += [
    path(r"accounts/", include("allauth.urls")),
    path(r"accounts/profile/", ProfileView.as_view(), name="user-profile"),
    path(r"accounts/account/", AccountView.as_view(), name="user-detail"),
    path(
        r"accounts/<slug:slug>/",
        ProfileDetailView.as_view(),
        name="profile-detail",  # noqa: E501
    ),
]

urlpatterns += [
    path(r"o/", include("oauth2_provider.urls", namespace="oauth2_provider"))
]

urlpatterns += activitypub_urlpatterns
urlpatterns += api_urlpatterns
