#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
Webfinger allows to discover information about a user based on resource name.
Returns a JRD (JSON Resource Descriptor) response.
"""

import logging

from django.contrib.sites.models import Site
from django.http import Http404
from rest_framework import generics
from rest_framework.response import Response

from webapp.models import Profile

logger = logging.getLogger(__name__)


class WebFingerView(generics.GenericAPIView):
    """
    WebFingerView provides discovery of user resources.
    It expects a 'resource' query parameter (e.g., 'acct:user@example.com')
    and returns a JRD response with 'application/jrd+json' content type.
    """

    model = Profile
    queryset = Profile.objects.all()  # Used by get_actor_for_webfinger
    template_name = "activitypub/webfinger.html"

    def get_actor_for_webfinger(self, resource_str: str):
        """
        Parses the WebFinger resource string, validates it, and retrieves
        the corresponding actor object.
        """
        if not resource_str:
            # This case should ideally be caught by the caller
            raise Http404("Resource parameter cannot be empty.")

        try:
            res_type, identifier = resource_str.split(":", 1)
        except ValueError:
            logger.debug(f"Invalid WebFinger resource format (no colon): '{resource_str}'")
            raise Http404(f"Invalid resource format: '{resource_str}'. Expected 'acct:user@domain'.")

        if res_type.lower() != "acct":
            logger.debug(f"Unsupported WebFinger resource scheme: '{res_type}' for resource '{resource_str}'")
            raise Http404(f"Unsupported resource scheme: '{res_type}'. Expected 'acct:'.")

        try:
            slug, host = identifier.split("@", 1)
        except ValueError:
            logger.debug(f"Invalid WebFinger account identifier (no @): '{identifier}' for resource '{resource_str}'")
            raise Http404(f"Invalid account identifier: '{identifier}'. Expected 'user@domain'.")

        current_domain = Site.objects.get_current().domain
        if host.lower() != current_domain.lower():
            logger.info(
                f"WebFinger request for domain '{host}' (from resource '{resource_str}') "
                f"does not match current site '{current_domain}'."
            )
            raise Http404(f"Resource domain '{host}' does not match this site.")

        try:
            # Assuming 'slug' on Profile model is the username part and should be unique case-insensitively.
            profile = self.queryset.get(slug__iexact=slug)
            if not hasattr(profile, 'actor') or not profile.actor:
                logger.warning(
                    f"Profile found for slug '{slug}' (from resource '{resource_str}') but no actor is associated."
                )
                raise Http404("User account is not fully configured for ActivityPub.")
            return profile.actor
        except Profile.DoesNotExist:
            logger.info(f"Profile with slug '{slug}' (from resource '{resource_str}') not found.")
            raise Http404("User not found.")
        except Exception as e:
            logger.error(f"Error retrieving profile/actor for slug '{slug}' (from resource '{resource_str}'): {e}")
            raise Http404("Error processing request for user.")

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        """
        Handles GET requests for WebFinger.
        """
        resource_param = request.query_params.get("resource")

        if not resource_param:
            return Response(
                {"error": "Missing resource parameter"},
                status=400,
                content_type="application/json"  # Error can be plain JSON
            )

        try:
            actor_instance = self.get_actor_for_webfinger(resource_param)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=404,
                content_type="application/json"  # Error can be plain JSON
            )

        base_domain = Site.objects.get_current().domain

        # --- Construct URLs for the template context ---
        # CRITICAL ASSUMPTION 1: actor_instance.id is the full ActivityPub ID URL.
        # If actor_instance.id is not a URL, you must change this to something like:
        # actor_ap_id_url = actor_instance.get_activitypub_id_url() or build it.
        # For example, if actor_instance.id is just a numeric ID:
        # actor_ap_id_url = f"https://{base_domain}/users/{actor_instance.slug}/activity" (adjust path)
        if not actor_instance.id or not isinstance(actor_instance.id, str) or not actor_instance.id.startswith('http'):
            logger.error(f"Actor ID '{actor_instance.id}' for resource '{resource_param}' is not a valid URL.")
            return Response({"error": "Server configuration error: Invalid Actor ID format."}, status=500, content_type="application/json")
        actor_ap_id_url = str(actor_instance.id) # Ensure it's a string

        # CRITICAL ASSUMPTION 2: actor_instance.profile exists and its get_absolute_url() returns a path.
        if not hasattr(actor_instance, 'profile') or not actor_instance.profile:
            logger.error(f"Actor (ID: {actor_instance.id}) for resource '{resource_param}' does not have an associated profile.")
            return Response({"error": "Server configuration error: Actor profile missing."}, status=500, content_type="application/json")

        if not hasattr(actor_instance.profile, 'get_absolute_url') or not callable(actor_instance.profile.get_absolute_url):
            logger.error(
                f"Actor's profile (ID: {actor_instance.profile.id}) for resource '{resource_param}' "
                f"is missing a callable get_absolute_url method."
            )
            return Response({"error": "Server configuration error: Actor profile URL method missing."}, status=500, content_type="application/json")

        try:
            profile_path = actor_instance.profile.get_absolute_url()
            if not profile_path.startswith('/'):
                profile_path = '/' + profile_path
            actor_html_url = f"https://{base_domain}{profile_path}"
        except Exception as e:
            logger.error(f"Error calling get_absolute_url for profile {actor_instance.profile.id}: {e}")
            return Response({"error": "Server configuration error: Could not determine profile URL."}, status=500, content_type="application/json")


        actor_avatar_url = None
        actor_avatar_media_type = None
        if hasattr(actor_instance.profile, 'imgurl') and actor_instance.profile.imgurl:
            # Assuming actor_instance.profile.imgurl is already a full, valid URL.
            # If it's a relative path, you'll need to prepend https://{base_domain}
            actor_avatar_url = actor_instance.profile.imgurl
            if isinstance(actor_avatar_url, str): # Basic check
                if '.png' in actor_avatar_url.lower():
                    actor_avatar_media_type = "image/png"
                elif '.jpg' in actor_avatar_url.lower() or '.jpeg' in actor_avatar_url.lower():
                    actor_avatar_media_type = "image/jpeg"
                elif '.gif' in actor_avatar_url.lower():
                    actor_avatar_media_type = "image/gif"
                # Add more types if needed, or store media_type in the model.
                # The template has a default if this remains None.

        context = {
            "resource": resource_param,
            "base": base_domain,
            "actor_ap_id_url": actor_ap_id_url,
            "actor_html_url": actor_html_url,
            "actor_avatar_url": actor_avatar_url,
            "actor_avatar_media_type": actor_avatar_media_type,
        }

        # Render the template using DRF's Response.
        # The content_type="application/jrd+json" is crucial.
        return Response(
            context,
            template_name=self.template_name,
            content_type="application/jrd+json"
        )
