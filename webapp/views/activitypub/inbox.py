#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
ActivityPub views to drive social interactions in pramari.de.

See::
    https://paul.kinlan.me/adding-activity-pub-to-your-static-site/
"""


import json
import logging

from django.http import JsonResponse
from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from webapp.models import Actor, Profile
from webapp.signature import SignatureChecker
from webapp.activities import follow, undo, create, delete, accept
from webapp.activity import ActivityMessage

from ...exceptions import ParseError  # noqa: E501
from ...exceptions import ParseJSONError, ParseUTF8Error

logger = logging.getLogger(__name__)


class InboxView(DetailView):
    """
    .. py:class:: webapp.views.InboxView

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

        :param request: The incoming request
        :param args: The positional arguments
        :param kwargs: The keyword arguments

        :return: tuple
            Actor: The target actor
            message: The parsed activity
            bool: The status of the signature verification
        """
        logger.debug(f"Request Headers: {request.headers}")
        signature = False

        target = self.get_object()  # this should work with DetailView?
        logger.error(target)

        try:
            # Assuming the request payload is a valid JSON activity
            body = request.body.decode("utf-8")
        except ValueError:
            message = "InboxView: Cannot decode utf-8"
            logger.error(message)
            raise ParseUTF8Error(message)

        try:
            activity = json.loads(body)
            activity = ActivityMessage(activity)
        except ValueError as e:
            message = f"InboxView: Received invalid JSON {e}"
            logger.error(message)
            raise ParseJSONError(message) from e
        except ParseError as e:
            logger.error(f"ParseError: {e}")
            raise e

        signature = SignatureChecker().validate(request)

        logger.debug(f"Signature: {signature}")

        return target, activity, signature

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
            target, message, signature = self.parse(request, args, kwargs)
        except ParseError as e:
            logger.debug("InboxView: ParseError %s", e)
            return JsonResponse({"error": str(e.message)}, status=400)

        if not signature:
            return JsonResponse({"error": "Invalid Signature"}, status=400)

        logger.debug(f"Activity Object: {message}")

        match message.get("type", None).lower():
            case "follow":
                result = follow(target=target, message=message)
            case "undo":
                result = undo(target=target, message=message)
            case "create":
                result = create(target=target, message=message)
            case "delete":
                result = delete(target=target, message=message)
            case "accept":
                result = accept(target=target, message=message)
            case _:
                error = f"InboxView: Unsupported activity: {message.type}"
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
        actor = self.get_object().actor
        assert request.method == "GET"
        assert request.path == f"{actor.inbox}"
        
        return JsonResponse({"status": f"{actor.inbox} ok"}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """
        Process the incoming message.

        No CSRF token required for incoming activities.
        """
        return super().dispatch(*args, **kwargs)
