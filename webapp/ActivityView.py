#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

import json
import uuid
import logging

from django.urls import reverse
from django.http import JsonResponse
from django.views.generic import View, ListView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from webapp.models import Profile

User = get_user_model()
logger = logging.getLogger(__name__)

###
"""
Below is Activitypub


"""


class WebFingerView(View):
    def get(self, r, *args, **kwargs):  # pylint: disable=W0613
        resource = r.GET.get("resource")

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

        username, domain = resource[5:].split("@")

        if not username:
            return JsonResponse({"error": "User not found"}, status=404)

        if domain != "pramari.de":
            return JsonResponse({"error": "Invalid domain."}, status=400)

        user = Profile.objects.filter(
            user__username=username
        ).first()  # pylint: disable=E1101

        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        webfinger_data = {
            "subject": f"acct:{user.user.username}@{r.get_host()}",
            "aliases": [
                f"https://{r.get_host()}{user.get_absolute_url}",
            ],
            "links": [
                {
                    "rel": "http://webfinger.net/rel/profile-page",
                    "type": "text/html",
                    "href": f"https://{r.get_host()}{user.get_absolute_url}",
                },
                {
                    "rel": "http://webfinger.net/rel/avatar",
                    "type": "image/jpeg",
                    "href": user.imgurl,
                },
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"https://{r.get_host()}{user.get_absolute_url}actor",  # noqa: E501
                },
                {
                    "rel": "http://ostatus.org/schema/1.0/subscribe",
                    "template": "https://pramari.de/authorize_interaction?uri={uri}",  # noqa: E501
                }
                # Add more link relations as needed
            ],
        }

        return JsonResponse(webfinger_data)


class ActorView(View):
    """
        path(
        r'accounts/<slug:slug>/activity',
        ActivityView.as_view(),
        name='activity-view'
    ),
    """

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        slug = kwargs.get("slug")

        profile = Profile.objects.get(slug=slug)  # pylint: disable=E1101

        return JsonResponse(profile.generate_jsonld())


class InboxView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def follow(self, request, activity, *args, **kwargs):
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
            follower_profile = Profile.objects.get(ap_id=activity["actor"])
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
