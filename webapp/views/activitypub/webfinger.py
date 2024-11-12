#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
Webfinger allows to discover information about a user based on resource name.
"""

import logging

# from django.http import JsonResponse
# from django.views import View
from rest_framework.response import Response
from django.contrib.sites.models import Site
from rest_framework import generics
from webapp.models import Profile
from webapp.renderers import JrdRenderer
from django.http import Http404

logger = logging.getLogger(__name__)


class WebFingerView(generics.GenericAPIView):
    """
    WebFingerView
    """

    model = Profile
    queryset = Profile.objects.all()
    template_name = "activitypub/webfinger.html"
    renderer_classes = [JrdRenderer]

    def get_object(self):
        resource = self.request.query_params.get("resource")
        if not resource:
            raise Http404({"error": "Missing resource parameter"})
        res, actor = resource.split(":")
        if res != "acct":
            raise Http404

        slug, host = actor.split("@")
        if host != Site.objects.get_current().domain:
            raise Http404
        return self.queryset.get(slug=slug).actor

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        """
        Response to GET Requests.
        """

        actor = self.get_object()

        base = f"{Site.objects.get_current().domain}"
        webfinger_data = {
            # The user's profile URL
            # subject is the user's profile identified
            # "subject": f"acct:{profile.user.username}@{request.get_host()}",
            "subject": f"acct:{actor.profile.user}@{base}",
            "aliases": [
                f"{actor.id}",
                f"https://{base}{actor.profile.get_absolute_url}",
            ],
            "links": [
                {
                    "rel": "http://webfinger.net/rel/profile-page",
                    "type": "text/html",
                    "href": f"https://{base}{actor.profile.get_absolute_url}",  # noqa: E501
                },
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"{actor.id}",  # noqa: E501
                },
                {
                    "rel": "http://ostatus.org/schema/1.0/subscribe",
                    "template": "https://pramari.de/authorize_interaction?uri={uri}",  # noqa: E501
                },
                {
                    "rel": "http://webfinger.net/rel/avatar",
                    "type": "image/jpeg",
                    "href": actor.profile.imgurl,
                },
            ],
        }
        if request.accepted_renderer.format == "html":
            data = {"base": base, "actor": self.get_object()}
            return Response(data, template_name=self.template_name)

        return Response(
            webfinger_data,
            content_type="application/jrd+json",
        )
