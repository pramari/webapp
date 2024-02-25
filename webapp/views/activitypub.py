#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
ActivityPub views to drive social interactions in pramari.de.

See::
    https://paul.kinlan.me/adding-activity-pub-to-your-static-site/
"""

import json
import uuid
import logging

from django.urls import reverse
from django.http import JsonResponse
from django.views.generic import View, ListView
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
                # {
                #     "rel": "http://webfinger.net/rel/profile-page",
                #     "type": "text/html",
                #     "href": f"https://{request.get_host()}{profile.get_actor_url}",  # noqa: E501
                # },
                # {
                #     "rel": "http://webfinger.net/rel/avatar",
                #     "type": "image/jpeg",
                #     "href": profile.imgurl,
                # },
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

        return JsonResponse(webfinger_data)


class ActorView(View):
    """
    Return the actor object for a given user.
    User is identified by the slug.

    Example urlconf:
        path(
        r'accounts/<slug:slug>/activity',
        ActivityView.as_view(),
        name='activity-view'
    ),
    """

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        """
        Return the actor object for a given user.
        Type:: GET
        Request: /accounts/<slug:slug>/activity

        """
        slug = kwargs.get("slug")

        profile = Profile.objects.get(slug=slug)  # pylint: disable=E1101

        return JsonResponse(profile.generate_jsonld())


class InboxView(View):
    """
    InboxView
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def follow(self, request, activity):
        """
        {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': 'https://neumeier.org/o/ca357ba56dc24554bfb7646a1db2c67f',
        'type': 'Follow',
        'actor': 'https://neumeier.org',
        'object': 'https://pramari.de/accounts/andreas/'
        }
        """

        from actstream.actions import follow

        # Store the follower in the database
        try:
            follower_profile = Profile.objects.get(ap_id=activity["actor"])  # noqa
        except Profile.DoesNotExist:
            """ """
            user = User.objects.get(username="AnonymousUser")
            follower_profile = Profile(ap_id=activity["actor"], user=user)
            follower_profile.save()

        profile_to_follow = Profile.objects.get(ap_id=activity["object"])
        # follower_profile.follows.add(profile_to_follow)

        follow(follower_profile, profile_to_follow, actor_only=False)

        # Optionally, you can send a response indicating
        # the success of the follow request
        # Generate a unique ID for the response
        response_id = str(uuid.uuid4())
        response = {
            "type": "Follow",
            "actor": request.build_absolute_uri(
                reverse("profile-detail", args=[follower_profile.slug])
            ),
            "object": request.build_absolute_uri(
                reverse("profile-detail", args=[profile_to_follow.slug])
            ),
            "id": response_id,
        }

        return JsonResponse(response)

    def post(self, request, *args, **kwargs):
        """
        process incoming activity.
        """

        # Process the incoming activity
        # Save the activity to the database, perform necessary actions, etc.
        # from .models import Activity
        from actstream import action as Activity

        try:
            # Assuming the request payload is a valid JSON activity
            body = request.body.decode("utf-8")
            activity = json.loads(body)  # Deserialize the JSON payload
        except ValueError:
            logger.error("InboxView: Invalid activity JSON")
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        print(type(activity))
        print(activity)
        print("---")

        activity_type = activity.get("type")
        activity_actor = activity.get("actor")
        activity_object = activity.get("object", {})

        match activity_type:
            case "Follow":
                return self.follow(request=request, activity=activity)
            case "Undo":
                raise NotImplementedError
            case "Create":
                # Save the Follow activity to the database

                follow_activity = Activity(
                    actor=activity_actor, verb="Follow", object=activity_object
                )
                follow_activity.save()
            case _:
                logger.error("Activity Actor: {}".format(activity_actor))
                logger.error("Activity Object: {}".format(activity_object))
                print(activity)
                follow_activity = Activity(
                    actor=activity_actor,
                    verb=f"Unkown: {activity_type}",
                    object=activity_object,
                )
                follow_activity.save()
                return JsonResponse(
                    {"error": "Invalid activity type"}, status=400
                )  # noqa: E501
        # Return a success response
        return JsonResponse({"status": "success"})


class OutboxView(View):
    def get(self, request, *args, **kwargs):
        # Retrieve the activity stream of the authenticated user's actor
        # ...

        slug = kwargs.get("slug")

        profile = Profile.objects.get(slug=slug)  # pylint: disable=E1101

        activity_list = profile.get_activities()

        # Prepare the activity stream response
        activity_stream = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollection",
            "totalItems": len(activity_list),
            "orderedItems": activity_list,
        }

        # Return the activity stream as a JSON response
        return JsonResponse(activity_stream)


class FollowView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # from .models import Activity
        from actstream import action as Activity

        try:
            # Assuming the request payload is a valid JSON activity
            activity = request.json
        except ValueError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Extract the relevant information from the Follow activity
        activity_actor = activity.get("actor")
        activity_object = activity.get("object")

        # Save the Follow activity to the database
        follow_activity = Activity(
            actor=activity_actor, verb="Follow", object=activity_object
        )
        follow_activity.save()

        # Perform additional actions, such as
        # establishing the follower relationship
        # ...

        # Return a success response
        return JsonResponse({"status": "success"})


class FollowersView(ListView):
    template_name = "activitypub/followers.html"

    def get_queryset(self):
        from django.shortcuts import get_object_or_404

        profile = get_object_or_404(Profile, slug=self.kwargs["slug"])
        return profile.followed_by.filter(consent=True)
        # .filter(user__is_verified=True)


class FollowingView(ListView):
    template_name = "activitypub/following.html"

    def get_queryset(self):
        from django.shortcuts import get_object_or_404

        profile = get_object_or_404(Profile, slug=self.kwargs["slug"])
        return profile.follows.filter(consent=True)
        # .filter(user__is_verified=True)
