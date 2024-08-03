#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
Webfinger allows to discover information about a user based on resource name.
"""

import logging
from django.http import JsonResponse
from django.views import View
from django.contrib.sites.models import Site
from ...models import Profile

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
                {"error": "Missing resource parameter"},
                status=400,
                content_type="application/jrd+json",
            )  # noqa: E501

        # Perform the necessary logic to retrieve user data
        # based on the provided resource

        if not resource.startswith("acct:"):
            return JsonResponse(
                {"error": "Invalid resource format"},
                status=400,
                content_type="application/jrd+json",
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

        base = f"{Site.objects.get_current().domain}"
        webfinger_data = {
            # The user's profile URL
            # subject is the user's profile identified
            # "subject": f"acct:{profile.user.username}@{request.get_host()}",
            "subject": f"acct:{profile.actor.actorID}",
            "aliases": [
                f"https://{base}{profile.actor.actorID}",
                f"https://{request.get_host()}{profile.get_absolute_url}",
            ],
            "links": [
                {
                    "rel": "http://webfinger.net/rel/profile-page",
                    "type": "text/html",
                    "href": f"https://{base}{profile.get_absolute_url}",  # noqa: E501
                },
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"https://{base}{profile.actor.actorID}",  # noqa: E501
                },
                {
                    "rel": "http://ostatus.org/schema/1.0/subscribe",
                    "template": "https://pramari.de/authorize_interaction?uri={uri}",  # noqa: E501
                },
                {
                    "rel": "http://webfinger.net/rel/avatar",
                    "type": "image/jpeg",
                    "href": profile.imgurl,
                },
            ],
        }

        return JsonResponse(
            webfinger_data,
            content_type="application/jrd+json",
        )
