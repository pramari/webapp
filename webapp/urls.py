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
from django.views.generic import TemplateView

from webapp.views import AddonView, AddonMsginfoView

from webapp.views import (
    StatusView,
    HealthCheckView,
    HomeView,
    GithubView,
    AccountView,
    ProfileView,
    ProfileDetailView,
    CalendarView,
    ContactView,
    SearchView,
)



logger = logging.getLogger(__name__)


urlpatterns = [
    path(r"", HomeView.as_view(), name="home"),
    path(r"ads.txt", TemplateView.as_view(template_name="ads.txt"), name="ads"),
    path(
        r"humans.txt", TemplateView.as_view(template_name="humans.txt"), name="humans"
    ),
    path(
        r"googlee7105c7cdfda4e14.html",
        TemplateView.as_view(template_name="googlee7105c7cdfda4e14.html"),
        name="google",
    ),
    path(r"calendar", CalendarView.as_view(), name="calendar"),
    path(r"contacts/", ContactView.as_view(), name="contacts"),
    path(
        r"contacts/people/<str:resourceName>/",
        ContactView.as_view(),
        {"resourceName": None},
        name="contact-detail",
    ),
    path(r"status/", cache_page(60)(StatusView.as_view()), name="status"),
    path(r"github/", GithubView.as_view(), name="github"),
    path(
        r"github/<str:username>/<str:repository>",
        GithubView.as_view(),
        name="github-detail",
    ),
    path(r"search/", SearchView.as_view(), name="search_result"),
]

urlpatterns += [
    path(r"accounts/", include("allauth.urls")),
    path(r"accounts/profile/", ProfileView.as_view(), name="user_profile"),
    path(r"accounts/account/", AccountView.as_view(), name="user-detail"),
    path(r"accounts/account/", AccountView.as_view(), name="user_account"),
    path(r"accounts/<slug:slug>/", ProfileDetailView.as_view(), name="profile-detail"),
]

urlpatterns += [
    path(r"o/", include("oauth2_provider.urls", namespace="oauth2_provider"))
]

urlpatterns += [
    path(r"addon/", AddonView.as_view(), name="addon"),
    path(r"addon/msginfo/", AddonMsginfoView.as_view(), name="addon-msginfo"),
]
