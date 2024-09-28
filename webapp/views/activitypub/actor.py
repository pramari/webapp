from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import DetailView
# from django.contrib.sites.models import Site
import logging

from webapp.models import Profile  # Profile is hosting Actor

logger = logging.getLogger(__name__)


class ActorView(DetailView):
    """
    Return the actor object for a given user.
    User is identified by the slug.

    :py:class:`webapp.models.activitypub.Actor` is the model that hosts the actor object.

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

    .. seealso::
        :py:mod:`webapp.urls.activitypub`

    """

    redirect_to = "profile-detail"
    model = Profile

    def to_jsonld(self, *args, **kwargs):
        actor = self.get_object().actor

        jsonld = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": actor.id,
            "type": "Person",
            "name": actor.profile.user.username,
            "preferredUsername": actor.profile.user.username,
            "summary": actor.profile.bio,
            "inbox": actor.inbox,
            "outbox": actor.outbox,
            "followers": actor.followers,
            "following": actor.following,
            "liked": actor.liked,
            "url": self.get_object().get_absolute_url,
            "manuallyApprovesFollowers": False,
            "discoverable": False,
            "indexable": False,
            "published": actor.profile.user.date_joined.isoformat(),
            "publicKey": {
                "id": actor.keyID,
                "owner": actor.id,
                "publicKeyPem": actor.profile.public_key_pem,
            },
            "image": {  # background image
                "type": "Image",
                "mediaType": "image/jpeg",
                "url": actor.profile.imgurl,
            },  # noqa: E501
            "icon": {
                "type": "Image",
                "mediaType": "image/png",
                "url": actor.profile.imgurl,
            },  # noqa: E501
        }
        from webapp.activity import canonicalize

        return canonicalize(jsonld)

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
