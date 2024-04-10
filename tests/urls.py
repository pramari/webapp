#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
URL configuration for the webapp module.

"""

from django.urls import path
from django.conf.urls import include

urlpatterns = [
    path(r"", include("webapp.urls")),
    path(r"", include("webapp.urls.api")),
    path(r"", include("webapp.urls.activitypub")),
]
