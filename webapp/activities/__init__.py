import logging
from webapp.models import Actor


from django.http import JsonResponse
from django.conf import settings


logger = logging.getLogger(__name__)


def action_decorator(f):
    def wrapper(target, *args, **kwargs):
        from actstream import action

        try:
            actor = Actor.objects.get(id=kwargs["message"].get("actor"))
        except Actor.DoesNotExist:
            logger.error(f"Actor not found: {kwargs['message']['actor']}")
            return JsonResponse({"error": "Actor not found"}, status=404)

        verb = kwargs["message"].get("type").lower()
        assert verb == f.__name__
        message = kwargs["message"]

        action.send(
            sender=actor, verb=verb, target=target, description=message
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


def undo(self, message: dict):
    """
    Undo an activity.
    """
    logger.error(f"Activity Object: {message}")

    if not message.get("id"):
        return JsonResponse({"status": "missing id"})

    if not message.get("object"):
        return JsonResponse({"status": "missing object"})

    if (
        not message.get("actor")
        and message.get("type").lower() != "follow"  # noqa: E501
    ):  # noqa: E501
        return JsonResponse({"status": "invalid object"})

    try:
        followers = (  # noqa: F841, E501
            Actor.objects.filter(ap_id=message.get("object"))
            .get()
            .followers  # noqa: E501
        )
    except Actor.DoesNotExist:
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
