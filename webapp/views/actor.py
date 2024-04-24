from django.http import JsonResponse
from django.views import View
from django.contrib.sites.models import Site

from ..models import Profile


class ActorView(View):
    """
    Return the actor object for a given user.
    User is identified by the slug.

    Example urlconf:
        path(
        r'accounts/<slug:slug>/actor',
        ActivityView.as_view(),
        name='activity-view'
    ),
    """

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        """
        Return the actor object for a given user
        represented in Activity Streams 2.0 JSON-LD.

        .. Type::
            GET

        .. Request::
            /accounts/<slug:slug>/actor

        .. Response::
            Activity Streams 2.0 JSON-LD
        """
        slug = kwargs.get("slug")

        profile = Profile.objects.get(slug=slug)  # pylint: disable=E1101

        base = f"https://{Site.objects.get_current().domain}"
        username = f"{profile.user.username}"  # pylint: disable=E1101
        actorid = f"{base}{profile.get_actor_url}"
        inbox = f"{base}{profile.get_inbox_url}"
        outbox = f"{base}{profile.get_outbox_url}"  # noqa: F841
        followers = f"{base}{profile.get_followers_url}"  # noqa: F841
        following = f"{base}{profile.get_following_url}"  # noqa: F841
        public_key = profile.get_public_key(base)

        jsonld = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": actorid,
            "type": "Person",
            "name": username,
            "preferredUsername": username,
            "summary": profile.bio,
            "inbox": inbox,
            "outbox": outbox,
            "followers": followers,
            "following": following,
            "publicKey": public_key,
            "image": {
                "type": "Image",
                "mediaType": "image/jpeg",
                "url": profile.imgurl,
            },  # noqa: E501
            "icon": {
                "type": "Image",
                "mediaType": "image/png",
                "url": profile.icon,
            },  # noqa: E501
        }

        return JsonResponse(
            jsonld,
            content_type="application/Activity+json",
        )
