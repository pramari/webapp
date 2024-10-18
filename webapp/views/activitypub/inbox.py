#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
ActivityPub views to drive social interactions in pramari.de.

See::
    https://paul.kinlan.me/adding-activity-pub-to-your-static-site/
"""


import logging

from django.http import JsonResponse
from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from webapp.models import Actor, Profile
from webapp.signature import SignatureChecker
from webapp.activities import follow, undo, create, delete, accept
from webapp.activity import ActivityObject

from ...exceptions import ParseError  # noqa: E501
from ...exceptions import ParseJSONError, ParseUTF8Error

logger = logging.getLogger(__name__)


class InboxView(DetailView):
    """
    .. py:class:: webapp.views.InboxView

    The inbox is discovered through the inbox property of an
    :py:class:webapp.models.activitypub.Actor's profile. The
    inbox **MUST** be an `OrderedCollection`.

    .. seealso::
        `ActivityPub Inbox <https://www.w3.org/TR/activitypub/#inbox>_`

    """

    model = Profile

    def parse(self, request, *args, **kwargs) -> tuple[Actor, dict, bool]:
        """
        Parse the incoming activity request.

        Fulfils two tasks:

        - Parse the incoming JSON activity
        - Verify the signature of the incoming activity

        Actor. The object that performed the activity.
        Verb. The verb phrase that identifies the action of the activity.
        Action Object. (Optional) The object linked to the action itself.
        Target. (Optional) The object to which the activity was performed.


        :param request: The incoming request
        :param args: The positional arguments
        :param kwargs: The keyword arguments

        :return: tuple
            bool: The status of the signature verification
            Actor: The actor object that performed the activity.
            Verb: The verb phrase that identifies the action of the activity.
            Action Object: The object linked to the action itself.
            Target: The object to which the activity was performed.
            message: The parsed activity
        """
        logger.debug(f"Request Headers: {request.headers}")

        try:
            # Assuming the request payload is a valid JSON activity
            body = request.body.decode("utf-8")
        except ValueError:
            message = "InboxView: Cannot decode utf-8"
            logger.error(message)
            raise ParseUTF8Error(message)

        try:
            import json

            message = json.loads(body)
            activity = ActivityObject(message)
        except ValueError as e:
            message = f"InboxView: Received invalid JSON {e}"
            logger.error(message)
            raise ParseJSONError(message) from e
        except ParseError as e:
            logger.error(f"ParseError: {e}")
            raise e

        signature = SignatureChecker().validate(request)
        logger.debug(f"Signature: {signature}")

        target = self.get_object()  # this should work with DetailView?

        return signature, activity, target

    def post(self, request, *args, **kwargs):
        """
        Process the incoming activity.

        First:
            - Parse the incoming request & Verify the signature
            - Get the actor for which the activity is intended

        Second:
            Dispatch to the appropriate method based on the activity type.
        """
        # Process the incoming activity

        try:
            signature, activity, target = self.parse(request, args, kwargs)
        except ParseError as e:
            logger.debug("InboxView: ParseError %s", e)
            return JsonResponse({"error": str(e.message)}, status=400)

        if not signature:
            return JsonResponse({"error": "Invalid Signature"}, status=400)

        logger.debug(f"Activity Object: {activity}")

        match activity.type.lower():
            case "follow":
                result = follow(target=target.actor, activity=activity)
            case "undo":
                result = undo(target=target.actor, activity=activity)
            case "create":
                result = create(target=target.actor, activity=activity)
            case "delete":
                result = delete(target=target.actor, activity=activity)
            case "accept":
                result = accept(target=target.actor, activity=activity)
            case _:
                error = f"InboxView: Unsupported activity: {activity.type}"
                logger.error(f"Actvity error: {error}")
                return JsonResponse({"error": error}, status=400)  # noqa: E501

        # Return a success response. Unclear, why.
        return JsonResponse({"status": f"success: {result}"})

    def get(self, request, *args, **kwargs):
        """
        Return a 200 for GET requests.

        Not sure this is necessary, but
        :py:meth:`webapp.tests.inbox.InboxTest.test_user_inbox` tests it.
        """
        from urllib.parse import urlparse

        actor = self.get_object().actor
        assert request.method == "GET"
        assert request.path == urlparse(actor.inbox).path

        if request.user.is_authenticated and request.user == actor.profile.user:
            return JsonResponse({"status": f"{actor.inbox} ok"}, status=200)
        return JsonResponse({"status": "not found"}, status=404)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """
        Process the incoming message.

        No CSRF token required for incoming activities.
        """
        return super().dispatch(*args, **kwargs)
