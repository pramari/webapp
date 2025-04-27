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
from webapp.activitypub.renderers import ActivityRenderer
from django.http import Http404

logger = logging.getLogger(__name__)


class WebFingerView(generics.GenericAPIView):
    """
    WebFingerView
    """

    model = Profile
    queryset = Profile.objects.all()
    template_name = "activitypub/webfinger.html"
    renderer_classes = [ActivityRenderer]

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

        data = {"base": base, "actor": actor}

        if request.accepted_renderer.format == "html":
            return Response(data, template_name=self.template_name)
        else:
            return Response(
            data, template_name=self.template_name,
            content_type="application/activity+json",
        )
