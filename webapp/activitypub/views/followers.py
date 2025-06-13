import json

from rest_framework import generics
from rest_framework.response import Response

from webapp.models import Profile
from webapp.encoders import UUIDEncoder


class FollowersView(generics.RetrieveAPIView):
    """
    Provide a list of followers for a given profile.

    Every actor SHOULD have a followers collection. This is a list of everyone
    who has sent a Follow activity for the actor, added as a side effect. This
    is where one would find a list of all the actors that are following the
    actor. The followers collection MUST be either an OrderedCollection or a
    Collection and MAY be filtered on privileges of an authenticated user or
    as appropriate when no authentication is given.

    .. note::
         The reverse for this view is `actor-followers`.
         The URL pattern `/accounts/<slug:slug>/followers/`

    .. seealso::
         The `W3C followers definition <https://www.w3.org/TR/activitystreams-vocabulary/#followers>`_.  # noqa

         `5.3 Followers Collection <https://www.w3.org/TR/activitypub/#followers>`_
    """

    # renderer_classes = [JsonLDRenderer, renderers.JSONRenderer]
    queryset = Profile.objects.all()
    lookup_field = "slug"

    # template_name = "activitypub/followers.html"
    paginate_by = 20
    model = Profile

    """
    def get_object(self, queryset=None):
        return get_object_or_404(Profile, slug=self.kwargs["slug"])

    def get_queryset(self):
        return self.get_object().actor.followed_by.all()
    """

    def followed_by(self):
        return self.get_object().actor.followed_by.all()

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        result = {
            "id": self.get_object().actor.followers,
            "type": "Collection",
            "totalItems": 0,
            "items": [],
        }
        followed_by = self.followed_by().values_list(
            "id", flat=True
        )  # .order_by("-created")
        result.update({"totalItems": len(followed_by)})
        result.update({"items": json.dumps(list(followed_by), cls=UUIDEncoder)})
        return Response(result, template_name="activitypub/followers.html")
