from django.http import JsonResponse, HttpResponseRedirect
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
        ```
        path(
        r'@<slug:slug>',
        ActorView.as_view(),
        name='actor-view')
        ```

    If the request header contains 'application/activity+json',
    the response will be in Activity Streams 2.0 JSON-LD format.
    Otherwise, the response will redirect the client to the `profile-page`.

    The actor object is a JSON-LD object that represents the user.

    .. seealso::
        `W3C Actor Objects <https://www.w3.org/TR/activitypub/#actor-objects>`_
        :py:mod:webapp.urls.activitypub

    """

    redirect_to = "profile-detail"
    model = Profile

    def to_jsonld(self, *args, **kwargs):
        base = f"https://{Site.objects.get_current().domain}"
        actor = self.get_object().actor_set.get()

        # assert f"{base}/@{slug}" == profile.actor.id

        actorid = f"{actor.id}"
        username = f"{actor.profile.user}"  # pylint: disable=E1101
        inbox = f"{base}{actor.inbox}"
        outbox = f"{base}{actor.outbox}"  # noqa: F841
        followers = f"{base}{actor.followers_url}"  # noqa: F841
        following = f"{base}{actor.following_url}"  # noqa: F841
        likes = f"{base}{actor.likes_url}"  # noqa: F841
        public_key = actor.profile.get_public_key(base)

        jsonld = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": actorid,
            "type": "Person",
            "name": username,
            "preferredUsername": username,
            "summary": actor.profile.bio,
            "inbox": inbox,
            "outbox": outbox,
            "followers": followers,
            "following": following,
            "likes": likes,
            "publicKey": public_key,
            "image": {
                "type": "Image",
                "mediaType": "image/jpeg",
                "url": actor.profile.imgurl,
            },  # noqa: E501
            "icon": {
                "type": "Image",
                "mediaType": "image/png",
                "url": actor.profile.icon,
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
        from django.urls import reverse

        return HttpResponseRedirect(
            reverse(self.redirect_to, kwargs={"slug": self.kwargs["slug"]})
        )
        # return super().get(request, *args, **kwargs)
