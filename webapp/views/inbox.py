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

# from taktivitypub import APObject, ObjectType

from webapp.models import Actor, Profile
from webapp.signals import action
from webapp.schema import ACTIVITY_TYPES

from ..exceptions import ParseError  # noqa: E501
from ..exceptions import ParseJSONError, ParseUTF8Error

logger = logging.getLogger(__name__)


def action_decorator(f):
    def wrapper(*args, **kwargs):
        try:
            actor = Actor.objects.get(id=kwargs["message"].get("actor"))
        except Actor.DoesNotExist:
            logger.error(f"Actor not found: {kwargs['message']['actor']}")
            return JsonResponse({"error": "Actor not found"}, status=404)
        try:
            target = Actor.objects.get(id=kwargs["message"].get("object"))
        except Actor.DoesNotExist:
            logger.error(f"Target not found: {kwargs['message']['object']}")
            return JsonResponse({"error": "Target not found"}, status=404)
        verb = kwargs["message"].get("type").lower()
        assert verb == f.__name__
        message = kwargs["message"]

        action.send(
            sender=actor, verb=verb, target=target, description=message
        )  # noqa: E501

        return f(*args, **kwargs)

    return wrapper


class InboxView(View):
    """
    InboxView

    Leveraging the Django Rest Framework to process incoming ActivityPub
    Messages, rely on `serializers:ActivitySerializer` to validate the
    incoming data.
    """

    @action_decorator
    def create(self, message: dict) -> JsonResponse:
        """
        Create a new something.
        """

        logger.error(f"Create Object: {message}")

        return JsonResponse(
            {
                "status": f"success: {message['actor']} {message['type']} {message['object']}"  # noqa: E501
            }  # noqa: E501
        )  # noqa: E501

    @action_decorator
    def accept(self, message: dict) -> JsonResponse:
        """
        Accept
        """

        return JsonResponse({"status": "accepted."})

    @action_decorator
    def delete(self, message: dict) -> JsonResponse:
        """
        Delete an activity.
        """

        return JsonResponse({"status": "cannot delete"})

    def undo(self, message: dict):
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

        if not message.get("id"):
            return JsonResponse({"status": "missing id"})

        if not message.get("object"):
            return JsonResponse({"status": "missing object"})

        if (
            not message.get("actor") and message.get("type").lower() != "follow"  # noqa: E501
        ):  # noqa: E501
            return JsonResponse({"status": "invalid object"})

        try:
            followers = (  # noqa: F841, E501
                Profile.objects.filter(ap_id=message.get("object"))
                .get()
                .followers  # noqa: E501
            )
        except Profile.DoesNotExist:
            return JsonResponse({"status": "no followers"})

        logger.error(f"{message['actor']} unfollowed {message['object']}")
        # followers.delete()

        return JsonResponse({"status": "undone"})

    def follow(self, message: dict):
        """{
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': 'https://neumeier.org/o/ca357ba56dc24554bfb7646a1db2c67f',
            'type': 'Follow',
            'actor': 'https://neumeier.org',
            'object': 'https://pramari.de/accounts/andreas/'
        }"""

        logger.debug(
            f"Activity: {message['actor']} wants to follow {message['object']}"
        )  # noqa: E501

        assert message["actor"] is not None

        # from webapp.tasks.activitypub import getRemoteActor

        # Step 1:
        # Create the actor profile in the database
        # and establish the follow relationship

        """
        remoteActor, created = Actor.objects.get_or_create(id=message.get('actor'))  # noqa: E501
        localActor = Actor.objects.get(id=message['object'])
        remoteActor.follows.set(localActor)
        if created:
            remoteActor.save()
        """

        # Step 2:
        # Confirm the follow request to message.actor
        from webapp.tasks.activitypub import acceptFollow

        """
        .. todo::
            - Check if the signature is valid
            - Store the follow request in the database
            - Defer the task to the background
        """
        if settings.DEBUG:
            acceptFollow(message)
        else:
            acceptFollow.delay(message)

        return JsonResponse(
            {
                "status": f"OK: {message['actor']} followed {message['object']}"  # noqa: E501
            }  # noqa: E501
        )

    def parse(self, request) -> tuple[dict, bool]:
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

        return activity, signature

    def post(self, request, *args, **kwargs):
        """
        Process the incoming activity.
        """
        # Process the incoming activity
        try:
            message, signature = self.parse(request)
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

        actor = None
        if message.get("actor") is not None:
            try:
                actor, created = Actor.objects.get_or_create(
                    id=message.get("actor")
                )  # noqa: E501
                if created:
                    actor.save()

            except Profile.DoesNotExist:
                logger.error(f"InboxView: Actor not found: {message['actor']}")
            except Profile.MultipleObjectsReturned:
                logger.error(
                    f"InboxView: Multiple actor profiles: {message['actor']}"
                )  # noqa: E501

        match message.get("type", None).lower():
            case "follow":
                result = self.follow(message=message)
            case "undo":
                result = self.undo(message=message)
            case "create":
                result = self.create(message=message)
            case "delete":
                result = self.delete(message=message)
            case "accept":
                result = self.accept(message=message)
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
