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
from ..activity import verifySignature

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

    def follow(self, message: APObject, signature: dict = None):
        """
        {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': 'https://neumeier.org/o/ca357ba56dc24554bfb7646a1db2c67f',
        'type': 'Follow',
        'actor': 'https://neumeier.org',
        'object': 'https://pramari.de/accounts/andreas/'
        }
        """

        """
        Find account to be followed.

        Ruby Code from Paul Kinlan:

              const signature = parseSignature(req);
              const actorInformation = await fetchActorInformation(signature.keyId);
              const signatureValid = verifySignature(signature, actorInformation.publicKey);

              if (signatureValid == null || signatureValid == false) {
                res.end('invalid signature');
                return;
              }

              // We should check the digest.
              if (message.type == "Follow") {
                // We are following.
                const followMessage: AP.Follow = <AP.Follow>message;
                if (followMessage.id == null) return;

                const collection = db.collection('followers');

                const actorID = (<URL>followMessage.actor).toString();
                const followDocRef = collection.doc(actorID.replace(/\//g, "_"));  # noqa: W605, E501
                const followDoc = await followDocRef.get();

                if (followDoc.exists) {
                  console.log("Already Following")
                  return res.end('already following');
                }

                // Create the follow;
                await followDocRef.set(followMessage);

                const guid = uuid();
                const domain = 'paul.kinlan.me';

                const acceptRequest: AP.Accept = <AP.Accept>{
                  "@context": "https://www.w3.org/ns/activitystreams",
                  'id': new URL(`https://${domain}/${guid}`),
                  'type': 'Accept',
                  'actor': "https://paul.kinlan.me/paul",
                  'object': followMessage
                };

                const actorInbox = new URL(actorInformation.inbox);

                const response = await sendSignedRequest(actorInbox, acceptRequest);  # noqa: E501

                console.log("Following result", response.status, response.statusText, await response.text());  # noqa: E501

                return res.end("ok")
              }
        """

        # Store the follower in the database
        logger.error(f"Activity: {message.actor} followed {message.object}")

        # message.object is the profile to be followed
        # it should be checked if local or remote

        # Step 2:
        # Confirm the follow reuqst to message.actor
        if not signature:
            """Not having a signature seems default?"""
            actor = {}  # getRemoteActor(message.actor)
        else:
            """
            .. todo:: Check the signature
            """
            actor = {}  # getRemoteActor(signature["keyId"])
            signatureValid = verifySignature(
                signature, actor.publicKey
            )  # noqa: F841, E501

        return JsonResponse(
            {
                "status": f"OK: {message.actor} followed {message.object} ({signatureValid})"  # noqa: E501
            }
        )

    def parse(self, request) -> tuple[APObject, dict]:
        signature = None
        try:
            # Assuming the request payload is a valid JSON activity
            body = request.body.decode("utf-8")
        except ValueError:
            message = "InboxView: Cannot decode utf-8"
            logger.error(message)
            raise ParseUTF8Error(message)

        try:
            js = json.loads(body)
        except ValueError as e:
            message = f"InboxView: Received invalid JSON {e}"
            logger.error(message)
            raise ParseJSONError(message)

        if "signature" in js.keys():
            signature = message.pop("signature")

        try:
            activity = APObject.load(js)
        except ValueError as e:
            message = f"InboxView: Invalid activity message: {e}"
            raise ParseActivityError(message) from e

        return activity, signature

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """
        Process the incoming message.

        No CSRF token required for incoming activities.
        """
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Process the incoming activity.
        """
        # Process the incoming activity
        try:
            message, signature = self.parse(request)
        except ParseError as e:
            logger.error(f"InboxView raised error: {e}")
            return JsonResponse({"error": str(e.message)}, status=400)

        # Process the activity based on its type

        logger.debug(f"Activity Object: {message}")
        logger.debug(f"Activity Signature: {signature}")

        try:
            match message.type:
                case ObjectType.Follow:
                    result = self.follow(message=message, signature=signature)
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
            return JsonResponse({"error": error}, status=400)  # noqa: E501

        # Return a success response. Unclear, why.
        return JsonResponse({"status": f"success: {result}"})
