#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
WebApp is a Django-based web application that provides models
and views for a user profiles and federation capaibilities in web
application.

:py:module:WebApp is a Django-based web application that provides models and
views for a web application. The WebApp is a Django-based web application
foundation providing user-profiles, user-roles, and user-permissions.
Along with that, it aims to add federation capabilities, such as ActivityPub.

`webapp` should really have been named `fedapp`.

In its structure, it is not different from other Django-based web applications.
"""

from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# from .celery import app as celery_app

__version__ = "1.1.24"
__date__ = "2024-07-17"
__author__ = "Andreas Neumeier"

contenttype = (
    "application/json+ld",
    "activity/json",
    "application/activity+json",
    "application/ld+json",
)

default_app_config = "webapp.apps.WebAppConfig"
