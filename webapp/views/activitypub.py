#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
ActivityPub views to drive social interactions in pramari.de.

See::
    https://paul.kinlan.me/adding-activity-pub-to-your-static-site/
"""

import logging

from django.urls import reverse
from django.http import JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from webapp.models import Profile

from .. import __version__


User = get_user_model()
logger = logging.getLogger(__name__)


class NodeInfoView(View):
    """
    Node Info.

    EndPoint::
        /.well-known/nodeinfo
    """

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        """
        Response to GET Requests.
        """
        r = {
            "links": [
                {
                    "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
                    "href": reverse("version"),
                }
            ]
        }
        return JsonResponse(r)


class VersionView(View):
    """
    VersionView

    endpoint::
        /api/v1/version
    """

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        """
        Response to GET Requests.
        """
        nodename = Site.objects.get_current().name
        total = len(Profile.objects.all())
        r = {
            "version": __version__,
            "software": {
                "name": __name__,
                "version": __version__,
            },
            "protocols": ["activitypub"],
            "services": {"outbound": [], "inbound": []},
            "usage": {
                "users": {
                    "total": total,
                    "activeMonth": 0,  # 251585,
                    "activeHalfyear": 0,  # 660001,
                },
                "localPosts": 0,  # 83554772,
            },
            "openRegistrations": False,
            "metadata": {
                "nodeName": nodename,
                "nodeDescription": "Private ActivityPub Server",
            },
        }
        return JsonResponse(r)


class FollowView(View):
    """
    .. todo::
        This is actually unused, is it?
        Most likely this is not from the standard.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # from .models import Activity
        try:
            # Assuming the request payload is a valid JSON activity
            activity = request.json
        except ValueError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Extract the relevant information from the Follow activity
        actor = activity.get("actor")
        object = activity.get("object")

        # Return a success response
        return JsonResponse({"status": f"success: {actor} followed {object}"})
