from django.http import JsonResponse
from django.views.generic import DetailView
from django.contrib.sites.models import Site
import logging

from webapp.models import Profile  # Profile is hosting Actor

logger = logging.getLogger(__name__)


class ActorView(DetailView):
    """
    Return the actor object for a given user.
    User is identified by the slug.

    Example urlconf:
        path(
        r'@<slug:slug>',
        ActivityView.as_view(),
        name='activity-view'
    )

    If the request header contains 'application/activity+json',
    the response will be in Activity Streams 2.0 JSON-LD format.
    Otherwise, the response will redirect the client to the `profile-page`.

    The actor object is a JSON-LD object that represents the user.
    https://www.w3.org/TR/activitypub/#actor-objects
    """

    redirect_to = "profile-detail"
    model = Profile

    def to_jsonld(self, *args, **kwargs):
        base = f"https://{Site.objects.get_current().domain}"
        profile = self.get_object()

        # assert f"{base}/@{slug}" == profile.actor.id

        username = f"{profile.user.username}"  # pylint: disable=E1101
        actorid = f"{base}/@{profile.slug}"
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
        return jsonld

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        if (
            "Accept" in request.headers
            and "application/activity+json"
            in request.headers.get("Accept")  # noqa: E501
        ):
            return JsonResponse(
                self.to_jsonld(request, *args, **kwargs),
                content_type="application/activity+json",
            )
        return super().get(request, *args, **kwargs)
