from django.http import JsonResponse, HttpResponseRedirect
from django.views import View
from django.contrib.sites.models import Site
import logging

from ..models import Profile
from ..mixins import JsonLDMixin

logger = logging.getLogger(__name__)


class ActorView(JsonLDMixin, View):
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
    """

    redirect_to = "user-detail"

    def to_jsonld(self, *args, **kwargs):
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

        return jsonld

    def oldget(self, request, *args, **kwargs):  # pylint: disable=W0613
        """
        Return the actor object for a given user
        represented in Activity Streams 2.0 JSON-LD.

        .. Type::
            GET

        .. Request::
            /@<slug:slug>

        .. Response::
            Activity Streams 2.0 JSON-LD if request header contains
            'application/activity+json'. Otherwise, it redirects to
            the `profile-page`.
        """
        slug = kwargs.get("slug")

        profile = Profile.objects.get(slug=slug)  # pylint: disable=E1101

        if (
            "Accept" in request.headers
            and "application/activity+json" in request.headers.get("Accept")
        ):
            return JsonResponse(
                self.to_jsonld(profile),
                content_type="application/activity+json",
            )
        else:
            return HttpResponseRedirect(profile.get_absolute_url)
