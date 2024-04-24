#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
Settings and Views for `Angry Planet Cloud`.
"""

from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# from .celery import app as celery_app

__version__ = "1.1.23"
__date__ = "2023-08-21"
__author__ = "Andreas Neumeier"

contenttype = (
    "application/json+ld",
    "activity/json",
    "application/activity+json",
    "application/ld+json",
)

default_app_config = "webapp.apps.WebAppConfig"
