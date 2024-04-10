#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
Webfinger allows to discover information about a user based on resource name.
"""

import logging
from django.http import JsonResponse
from django.views import View
from ..models import Profile

logger = logging.getLogger(__name__)


class WebFingerView(View):
    """
    WebFingerView
    """

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        """
        Response to GET Requests.
        """
        resource = request.GET.get("resource")

        if not resource:
            return JsonResponse(
                {"error": "Missing resource parameter"}, status=400
            )  # noqa: E501

        # Perform the necessary logic to retrieve user data
        # based on the provided resource

        if not resource.startswith("acct:"):
            return JsonResponse(
                {"error": "Invalid resource format"}, status=400
            )  # noqa: E501

        try:
            username, domain = resource[5:].split("@")
        except ValueError:
            logger.debug(
                "WebFingerView: ValueError. Assuming domain for actor is pramari.de"  # noqa: E501
            )
            username = resource[5:]
            domain = "pramari.de"

        if not username:
            return JsonResponse({"error": "User not found"}, status=404)

        if domain != "pramari.de":
            return JsonResponse({"error": "Invalid domain."}, status=400)

        try:
            profile = Profile.objects.filter(  # pylint: disable=E1101
                user__username=username
            ).get()  # pylint: disable=E1101
        except Profile.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        webfinger_data = {
            # The user's profile URL
            # subject is the user's profile identified
            "subject": f"acct:{profile.user.username}@{request.get_host()}",
            "aliases": [
                f"https://{request.get_host()}{profile.get_absolute_url}",
                f"https://{request.get_host()}{profile.get_actor_url}",
            ],
            "links": [
                {
                    "rel": "http://webfinger.net/rel/profile-page",
                    "type": "text/html",
                    "href": f"https://{request.get_host()}{profile.get_absolute_url}",  # noqa: E501
                },
                {
                    "rel": "http://webfinger.net/rel/avatar",
                    "type": "image/jpeg",
                    "href": profile.imgurl,
                },
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"https://{request.get_host()}{profile.get_actor_url}",  # noqa: E501
                },
                # {
                #    "rel": "http://ostatus.org/schema/1.0/subscribe",
                #    "template": "https://pramari.de/authorize_interaction?uri={uri}",  # noqa: E501
                # },
            ],
        }

        return JsonResponse(
            webfinger_data,
            content_type="application/jrd+json",
        )
