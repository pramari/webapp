import logging
from webapp.models import Actor


from django.http import JsonResponse
from django.conf import settings
from webapp.activity import ActivityObject
from webapp.tasks.activitypub import getRemoteActor
from webapp.signals import action


logger = logging.getLogger(__name__)


def action_decorator(f):
    def wrapper(target, activity: ActivityObject, *args, **kwargs):
        try:
            localactor = Actor.objects.get(id=activity.actor)
        except Actor.DoesNotExist:
            logger.error(f"Actor not found: '{activity.actor}'")
            return JsonResponse({"error": "Actor f'{activity.actor}' not found"}, status=404)

        try:
            action_object = Actor.objects.get(id=activity.object)
        except Actor.DoesNotExist:
            logger.error(f"Object not found: '{activity.object}'")
            return JsonResponse({"error": "Actor f'{activity.object}' not found"}, status=404)

        action.send(
            sender=localactor, verb=activity.type, action_object=action_object, target=target
        )  # noqa: E501

        return f(*args, **kwargs)

    return wrapper


@action_decorator
def create(self, target, message: dict) -> JsonResponse:
    """
    Create a new `:model:Note`.

    Type: Note
        {
        'id': 'https://23.social/users/andreasofthings/statuses/112728133944821188',
        'type': 'Note',
        'summary': None,
        'inReplyTo': None,
        'published': '2024-07-04T12:06:57Z',
        'url': 'https://23.social/@andreasofthings/112728133944821188',
        'attributedTo': 'https://23.social/users/andreasofthings',
        'to': ['https://www.w3.org/ns/activitystreams#Public'],
        'cc': ['https://23.social/users/andreasofthings/followers'],
        'sensitive': False,
        'atomUri': 'https://23.social/users/andreasofthings/statuses/112728133944821188',
        'inReplyToAtomUri': None,
        'conversation': 'tag:23.social,2024-07-04:objectId=4444254:objectType=Conversation',
        'content': '<p>I implemented http signatures (both sign and verify) for the fediverse.</p><p>In python.</p><p>I feel like I made fire.</p>',
        'contentMap': {'en': '<p>I implemented http signatures (both sign and verify) for the fediverse.</p><p>In python.</p><p>I feel like I made fire.</p>'},
        'attachment': [],
        'tag': [],
        'replies': {
            'id': 'https://23.social/users/andreasofthings/statuses/112728133944821188/replies',
            'type': 'Collection',
            'first': {
                'type': 'CollectionPage',
                'next': 'https://23.social/users/andreasofthings/statuses/112728133944821188/replies?only_other_accounts=true&page=true',
                'partOf': 'https://23.social/users/andreasofthings/statuses/112728133944821188/replies',
                'items': []
            }
        }
    }  # noqa: E501
    """

    logger.error(f"Create Object: {message}")

    note = message.get("object")
    if note.type == "Note":
        from webapp.models import Note

        localNote = Note.objects.create(  # noqa: F841
            remoteID=note.get("id"),
            content=note.get("content"),
            published=note.get("published"),
        )  # noqa: F841

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


@action_decorator
def undo(target: Actor, activity: ActivityObject):
    """
    Undo an activity.
    """
    logger.error(f"Activity Object: {activity}")

    if not activity.id:
        return JsonResponse({"status": "missing id"})

    if not activity.object:
        return JsonResponse({"status": "missing object"})

    if (
        not activity.actor
        and activity.type.lower() != "follow"  # noqa: E501
    ):  # noqa: E501
        return JsonResponse({"status": "invalid object"})

    try:
        followers = (  # noqa: F841, E501
            Actor.objects.filter(id=activity.object)
            .get()
            .followers  # noqa: E501
        )
    except Actor.DoesNotExist:
        return JsonResponse({"status": "no followers"})

    logger.error(f"{activity.actor} has undone {activity.object}")
    # followers.delete()

    return JsonResponse({"status": "undone"})


@action_decorator
def follow(target: Actor, activity: ActivityObject):
    """

    :param target: The target of the activity
    :param activity: The :py:class:webapp.activity.Activityobject`

    .. example:: Follow Activity {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': 'https://neumeier.org/o/ca357ba56dc24554bfb7646a1db2c67f',
        'type': 'Follow',
        'actor': 'https://neumeier.org',
        'object': 'https://pramari.de/accounts/andreas/'
    }

    """

    logger.debug(
        f"Activity: {activity.actor} wants to follow {activity.object}"
    )  # noqa: E501

    assert activity.actor is not None

    # Step 1:
    # Create the actor profile in the database
    # and establish the follow relationship
    remoteActor = getRemoteActor(activity.actor)
    remoteActorObject = Actor.objects.get(id=remoteActor.get("id"))
    localActorObject = Actor.objects.get(id=activity.object)
    remoteActorObject.follows.add(localActorObject) 

    # Step 2:
    # Confirm the follow request to message.actor
    from webapp.tasks.activitypub import acceptFollow

    """
    .. todo::
        - Check if the signature is valid
        - Store the follow request in the database
        - Defer the task to the background
    """
    action_id = action.send(
        sender=localActorObject, verb="Accept", action_object=remoteActorObject
    )  # noqa: E501, BLK100

    if settings.DEBUG:
        acceptFollow(remoteActor.inbox, activity, action_id[0][1].id)
    else:
        acceptFollow.delay(remoteActor.inbox, activity, action_id[0][1].id)

    return JsonResponse(
        {
            "status": f"OK: {activity.actor} followed {activity.object}"  # noqa: E501
        }  # noqa: E501
    )
