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
from rest_framework.exceptions import ParseError
from django.contrib.sites.models import Site
from rest_framework import generics
from webapp.models import Profile
from django.http import Http404
from webapp.activitypub.serializers import ActorSerializer
from webapp.activitypub.renderers import (JrdRenderer) #, JsonLDRenderer, ActivityRenderer)

logger = logging.getLogger(__name__)


class WebFingerView(generics.GenericAPIView):
    """
    WebFingerView
    """

    model = Profile
    queryset = Profile.objects.all()
    renderer_classes = (
        JrdRenderer,
        # JsonLDRenderer,
        # ActivityRenderer,
        #
    )

    def get_object(self, *args, **kwargs):
        slug, host = kwargs.get("actor", "").split("@")
        if host != Site.objects.get_current().domain:
            raise Http404
        try:
            actor = self.queryset.get(slug=slug).actor
        except Profile.DoesNotExist:
            raise Http404
        return actor

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        """
        Response to GET Requests.
        """
        resource = self.request.query_params.get("resource")

        if not resource:
            raise ParseError("Missing resource parameter")

        res, actor = resource.split(":")
        if res != "acct":
            raise ParseError("Invalid resource type: {}".format(res))

        actor_object = self.get_object(actor=actor)
        base = f"{Site.objects.get_current().domain}"

        if actor_object:
            serialized_actor = ActorSerializer(actor_object).data
        else:
            serialized_actor = None


        if request.accepted_renderer.format == "html":
            data = {"base": base, "actor": serialized_actor}
            return Response(data, template_name=self.template_name)
        else:

            template =  {
                "subject": f"{resource}",
                "aliases": [
                    actor_object.id,
                    resource
                ],
                "properties": {
                    "http://schemas.google.com/g/2010#updates-from": actor_object.inbox
                },
                "links": [
                    {
                        "rel": "self",
                        "type": "application/activity+json",
                        "href": actor_object.id
                    },
                    {
                        "rel": "http://webfinger.net/rel/profile-page",
                        "type": "text/html",
                        "href": actor_object.id
                    }
                ]
            }

            return Response(template)
