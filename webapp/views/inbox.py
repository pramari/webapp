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
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

# from taktivitypub import APObject, ObjectType

from webapp.models import Actor, Profile
from webapp.schema import ACTIVITY_TYPES
from webapp.activities import follow, undo, create, delete, accept

from ..exceptions import ParseError  # noqa: E501
from ..exceptions import ParseJSONError, ParseUTF8Error

logger = logging.getLogger(__name__)


class InboxView(DetailView):
    """
    InboxView

    Leveraging the Django Rest Framework to process incoming ActivityPub
    Messages, rely on `serializers:ActivitySerializer` to validate the
    incoming data.
    """

    model = Profile

    def parse(self, request, *args, **kwargs) -> tuple[Actor, dict, bool]:
        """
        Parse the incoming activity request.
        Fulfils two tasks:
            - Parse the incoming JSON activity
            - Verify the signature of the incoming activity

        Parameters::

            request (Request): The incoming request

        Returns::

            dict: The parsed activity
            bool: The status of the signature verification
        """
        logger.debug(f"Request Headers: {request.headers}")
        signature = False

        actorObject = get_object_or_404(Profile, id=kwargs.get("slug"))  # noqa: F841, E501

        try:
            # Assuming the request payload is a valid JSON activity
            body = request.body.decode("utf-8")
        except ValueError:
            message = "InboxView: Cannot decode utf-8"
            logger.error(message)
            raise ParseUTF8Error(message)

        try:
            # js = json.loads(body)
            activity = json.loads(body)
        except ValueError as e:
            message = f"InboxView: Received invalid JSON {e}"
            logger.error(message)
            raise ParseJSONError(message) from e

        # from webapp.activity import ActivityMessage

        # activity = ActivityMessage(activity)

        assert activity is not None
        assert activity["type"] is not None
        assert activity["type"].lower() in ACTIVITY_TYPES.keys()

        """
        try:
            activity = APObject.load(js)
        except ValueError as e:
            message = f"InboxView: Invalid activity message: {e}"
            logger.error(message)
            raise ParseActivityError(message) from e
        """

        """
        .. todo::
            - Verify the signature of the incoming activity
        """
        from webapp.signature import SignatureChecker

        signature = SignatureChecker().validate(request)

        logger.debug(f"Signature: {signature}")

        return actorObject, activity, signature

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
            actor, message, signature = self.parse(request, args, kwargs)
        except ParseError as e:
            logger.debug(f"InboxView: ParseError {e}")
            return JsonResponse({"error": str(e.message)}, status=400)

        if not signature:
            """
            If the signature is not valid, return an error.
            """
            logger.debug(
                "InboxView: Invalid Signature %s", message["actor"]
            )  # noqa: E501
            return JsonResponse({"error": "Invalid Signature"}, status=400)

        # Process the activity based on its type
        logger.debug(f"Activity Object: {message}")

        match message.get("type", None).lower():
            case "follow":
                result = follow(message=message)
            case "undo":
                result = undo(message=message)
            case "create":
                result = create(message=message)
            case "delete":
                result = delete(message=message)
            case "accept":
                result = accept(message=message)
            case _:
                error = f"InboxView: Unsupported activity: {message.type}"
                logger.error(f"Actvity error: {error}")
                return JsonResponse({"error": error}, status=400)  # noqa: E501

        # Return a success response. Unclear, why.
        return JsonResponse({"status": f"success: {result}"})

    def get(self, request, *args, **kwargs):
        """
        Return a 404 for GET requests.
        """
        return JsonResponse({"error": "Not found"}, status=404)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """
        Process the incoming message.

        No CSRF token required for incoming activities.
        """
        return super().dispatch(*args, **kwargs)
