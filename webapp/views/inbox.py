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

from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from taktivitypub import APObject, ObjectType

from ..exceptions import (
    ParseActivityError,
    ParseError,  # noqa: E501
    ParseJSONError,
    ParseUTF8Error,
)
from ..models import Profile

# from ..activity import verifySignature

logger = logging.getLogger(__name__)


class InboxView(View):
    """
    InboxView

    Leveraging the Django Rest Framework to process incoming ActivityPub
    Messages, rely on `serializers:ActivitySerializer` to validate the
    incoming data.
    """

    def create(self, request, message: APObject) -> JsonResponse:
        """
        Create a new something.
        """
        actor = message.actor
        type = message.type
        object = message.object

        logger.debug("This happened: %s %s %s", actor, type, object)

        return JsonResponse({"status": f"success: {actor} {type} {object}"})

    def delete(self, request, message: APObject) -> JsonResponse:
        """
        Delete an activity.
        """

        if message.signature.is_valid():
            logger.error(f"Activity Signature: {message.signature}")
            return JsonResponse({"status": f"success: deleted {object}"})

        return JsonResponse({"status": "cannot delete"})

    def undo(self, request, message: APObject):
        """
        Undo an activity.

        Ruby from Paul Kinlan:
            // Undo a follow.
            const undoObject: AP.Undo = <AP.Undo>message;
            if (undoObject == null || undoObject.id == null) return;
            if (undoObject.object == null) return;
            if ("actor" in undoObject.object == false
                && (<CoreObject>undoObject.object).type != "Follow") return;

            const docId = undoObject.actor.toString().replace(/\//g, "_");  # noqa: W605, E501
            const res = await db.collection('followers').doc(docId).delete();

            console.log("Deleted", res)
        """
        logger.error(f"Activity Object: {message}")

        if message.id is None:
            return JsonResponse({"status": "missing id"})

        if message.object is None:
            return JsonResponse({"status": "missing object"})

        if (
            "actor" not in message.object
            and message.object.type is not ObjectType.Follow
        ):  # noqa: E501
            return JsonResponse({"status": "invalid object"})

        docId = message.actor.replace("/", "_")  # noqa: F841

        try:
            followers = (  # noqa: F841, E501
                Profile.objects.filter(ap_id=message.object).get().followers
            )
        except Profile.DoesNotExist:
            return JsonResponse({"status": "no followers"})

        logger.error(f"{message.actor} unfollowed {object}")
        # followers.delete()

        return JsonResponse({"status": "undone"})

    def follow(self, message: APObject):
        """{
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': 'https://neumeier.org/o/ca357ba56dc24554bfb7646a1db2c67f',
            'type': 'Follow',
            'actor': 'https://neumeier.org',
            'object': 'https://pramari.de/accounts/andreas/'
        }"""

        # Store the follower in the database
        logger.debug(
            f"Activity: {message.actor} wants to follow {message.object}"
        )  # noqa: E501

        assert message.actor is not None

        from webapp.tasks.activitypub import getRemoteActor

        try:
            remoteActor = getRemoteActor(message.actor)  # noqa: F841
        except Exception as e:
            logger.error(f"Error getting remote actor: {e}")
            return JsonResponse({"error": "Error getting remote actor"})

        # Step 2:
        # Confirm the follow request to message.actor
        from webapp.tasks.activitypub import accept_follow

        """
        .. todo::
            - Check if the signature is valid
            - Store the follow request in the database
            - Defer the task to the background
        """
        try:
            if settings.DEBUG:
                accept_follow(remoteActor, message.object)
            else:
                accept_follow.delay(remoteActor, message.object)
        except Exception as e:
            logger.error(f"Error accepting follow request: {e}")
            return JsonResponse({"error": "Error accepting follow request"})

        return JsonResponse(
            {"status": f"OK: {message.actor} followed {message.object}"}  # noqa: E501
        )

    def parse(self, request) -> tuple[APObject, bool]:
        logger.error(f"Request: {request.headers}")
        signature = False
        try:
            # Assuming the request payload is a valid JSON activity
            body = request.body.decode("utf-8")
        except ValueError:
            message = "InboxView: Cannot decode utf-8"
            logger.error(message)
            raise ParseUTF8Error(message)

        try:
            logger.error(f"Body: {body}")
            js = json.loads(body)
        except ValueError as e:
            message = f"InboxView: Received invalid JSON {e}"
            logger.error(message)
            raise ParseJSONError(message) from e

        try:
            activity = APObject.load(js)
        except ValueError as e:
            message = f"InboxView: Invalid activity message: {e}"
            logger.error(message)
            raise ParseActivityError(message) from e

        """
        .. todo::
            - Verify the signature of the incoming activity
        """
        from webapp.signature import SignatureChecker

        signature = SignatureChecker().validate(request)
        logger.error(f"Signature: {signature}")
        return activity, signature

    def post(self, request, *args, **kwargs):
        """
        Process the incoming activity.
        """
        # Process the incoming activity
        try:
            message, signature = self.parse(request)
        except ParseError as e:
            logger.debug(f"InboxView raised error: {e}")
            return JsonResponse({"error": str(e.message)}, status=400)

        if not signature:
            """
            If the signature is not valid, return an error.
            """
            logger.error(
                "InboxView: Invalid Actor Signature from %s", message.actor
            )  # noqa: E501
            return JsonResponse({"error": "Invalid Signature"}, status=400)

        # Process the activity based on its type

        logger.debug(f"Activity Object: {message}")

        try:
            match message.type:
                case ObjectType.Follow:
                    result = self.follow(message=message)
                case ObjectType.Undo:
                    result = self.undo(request=request, message=message)
                case ObjectType.Create:
                    result = self.create(request=request, message=message)
                case ObjectType.Delete:
                    result = self.delete(request=request, message=message)
                case _:
                    error = f"InboxView: Unsupported activity: {message.type}"
                    logger.error(f"Actvity error: {error}")
        except Exception as e:
            error = f"InboxView: Error processing activity: {e}"
            logger.error(error)
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
