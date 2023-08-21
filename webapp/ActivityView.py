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
    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        resource = request.GET.get("resource")

        if not resource:
            return JsonResponse(
                {"error": "Missing resource parameter"},
                status=400
            )

        # Perform the necessary logic to retrieve user data
        # based on the provided resource

        if not resource.startswith("acct:"):
            return JsonResponse(
                {"error": "Invalid resource format"},
                status=400
            )

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
            "subject": f"acct:{user.user.username}@{request.get_host()}",
            "aliases": [
                f"https://{request.get_host()}{user.get_absolute_url}",
            ],
            "links": [
                {
                    "rel": "http://webfinger.net/rel/profile-page",
                    "type": "text/html",
                    "href": f"https://{request.get_host()}{user.get_absolute_url}",
                },
                {
                    "rel": "http://webfinger.net/rel/avatar",
                    "type": "image/jpeg",
                    "href": user.imgurl,
                },
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"https://{request.get_host()}{user.get_absolute_url}actor",
                },
                {
                    "rel": "http://ostatus.org/schema/1.0/subscribe",
                    "template": "https://pramari.de/authorize_interaction?uri={uri}",
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
            follower_profile = Profile.objects.get(
                ap_id=activity['actor']
            )
        except Profile.DoesNotExist:
            """
            Traceback (most recent call last):
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/asgiref/sync.py", line 534, in thread_handler
                    raise exc_info[1]    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/core/handlers/exception.py", line 42, in inner
                    response = await get_response(request)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/core/handlers/base.py", line 253, in _get_response_async      response = await wrapped_callback(    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/asgiref/sync.py", line 479, in __call__      ret: _R = await loop.run_in_executor(    
                File "/layers/google.python.runtime/python/lib/python3.10/concurrent/futures/thread.py", line 58, in run      result = self.fn(*self.args, **self.kwargs)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/asgiref/sync.py", line 538, in thread_handler      return func(*args, **kwargs)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/views/generic/base.py", line 104, in view      return self.dispatch(request, *args, **kwargs)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/utils/decorators.py", line 46, in _wrapper      return bound_method(*args, **kwargs)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/views/decorators/csrf.py", line 56, in wrapper_view      return view_func(*args, **kwargs)    
                File "/workspace/webapp/ActivityView.py", line 113, in dispatch      return super().dispatch(*args, **kwargs)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/views/generic/base.py", line 143, in dispatch      return handler(request, *args, **kwargs)    
                File "/workspace/webapp/ActivityView.py", line 256, in post      
                    return self.follow(request=request, activity=activity)    
                File "/workspace/webapp/ActivityView.py", line 183, in follow      
                    follow(follower_profile, profile_to_follow, actor_only=False)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/actstream/actions.py", line 35, in follow      instance, created = apps.get_model('actstream', 'follow').objects.get_or_create(    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/db/models/manager.py", line 87, in manager_method      return getattr(self.get_queryset(), name)(*args, **kwargs)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/db/models/query.py", line 916, in get_or_create      return self.get(**kwargs), False    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/db/models/query.py", line 623, in get      clone = self._chain() if self.query.combinator else self.filter(*args, **kwargs)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/db/models/query.py", line 1436, in filter      return self._filter_or_exclude(False, args, kwargs)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/db/models/query.py", line 1454, in _filter_or_exclude      clone._filter_or_exclude_inplace(negate, args, kwargs)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/db/models/query.py", line 1461, in _filter_or_exclude_inplace      self._query.add_q(Q(*args, **kwargs))    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/db/models/sql/query.py", line 1534, in add_q      clause, _ = self._add_q(q_object, self.used_aliases)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/db/models/sql/query.py", line 1565, in _add_q      child_clause, needed_inner = self.build_filter(    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/db/models/sql/query.py", line 1453, in build_filter      self.check_related_objects(join_info.final_field, value, join_info.opts)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/db/models/sql/query.py", line 1264, in check_related_objects      self.check_query_object_type(value, opts, field)    
                File "/layers/google.python.pip/pip/lib/python3.10/site-packages/django/db/models/sql/query.py", line 1241, in check_query_object_type      raise ValueError(  ValueError: Cannot query "AnonymousUser": Must be "User" instance.

            """
            user = User.objects.get(username="AnonymousUser")
            follower_profile = Profile(
                ap_id=activity['actor'],
                user=user
            )
            follower_profile.save()

        profile_to_follow = Profile.objects.get(
            ap_id=activity['object']
        )
        # follower_profile.follows.add(profile_to_follow)
        
        follow(follower_profile, profile_to_follow, actor_only=False)

        # Optionally, you can send a response indicating
        # the success of the follow request
        # Generate a unique ID for the response
        response_id = str(uuid.uuid4())
        response = {
            "type": "Follow",
            "actor": request.build_absolute_uri(
                reverse(
                    "profile-detail",
                    args=[follower_profile.slug]
                )
            ),
            "object": request.build_absolute_uri(
                reverse(
                    "profile-detail",
                    args=[profile_to_follow.slug]
                )
            ),
            "id": response_id,
        }

        return JsonResponse(response)

    def undo(self, request, activity, *args, **kwargs):
        """
        {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': 'https://neumeier.org/o/dba3005c4ecc406c8f7d4c948fa1f337',
            'type': 'Undo',
            'actor': 'https://neumeier.org',
            'object': {
                'id': 'https://neumeier.org/o/97389b99a50049a8b061d792329088f4',
                'type': 'Follow',
                'actor': 'https://neumeier.org',
                'object': 'https://pramari.de/accounts/andreas/'}
        }
        """
        response_id = str(uuid.uuid4())
        response = {
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
            body = request.body.decode('utf-8')
            activity = json.loads(body)  # Deserialize the JSON payload
        except ValueError:
            logger.error("InboxView: Invalid activity JSON")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        print(type(activity))
        print(activity)
        print("---")

        activity_type = activity.get('type')
        activity_actor = activity.get('actor')
        activity_object = activity.get('object', {})

        match activity_type:
            case 'Follow':
                return self.follow(request=request, activity=activity)
            case 'Undo':
                return self.undo(request=request, activity=activity)
            case 'Create':
                # Save the Follow activity to the database

                follow_activity = Activity(
                    actor=activity_actor,
                    verb='Follow',
                    object=activity_object
                )
                follow_activity.save()
            case _:
                logger.error("Activity Actor: {}".format(activity_actor))
                logger.error("Activity Object: {}".format(activity_object))
                print(activity)
                follow_activity = Activity(
                    actor=activity_actor,
                    verb=f'Unkown: {activity_type}',
                    object=activity_object
                )
                follow_activity.save()
                return JsonResponse({
                    "error": "Invalid activity type"
                }, status=400)

        # Return a success response
        return JsonResponse({'status': 'success'})


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
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Extract the relevant information from the Follow activity
        activity_actor = activity.get('actor')
        activity_object = activity.get('object')

        # Save the Follow activity to the database
        follow_activity = Activity(
            actor=activity_actor,
            verb='Follow',
            object=activity_object
        )
        follow_activity.save()

        # Perform additional actions, such as
        # establishing the follower relationship
        # ...

        # Return a success response
        return JsonResponse({'status': 'success'})


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
