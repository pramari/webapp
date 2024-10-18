from rest_framework import generics
import json
from rest_framework.response import Response
from webapp.encoders import UUIDEncoder
from webapp.models import Profile


class FollowingView(generics.RetrieveAPIView):
    """
    Provide a list of who this profile is following.

    ```
    Every actor SHOULD have a following collection. This is a list of
    everybody that the actor has followed, added as a side effect. The
    following collection MUST be either an OrderedCollection or a Collection
    and MAY be filtered on privileges of an authenticated user or as
    appropriate when no authentication is given.
    ```

    .. note::
         The reverse for this view is `actor-following`.
         The URL pattern `/accounts/<slug:slug>/following/`

    .. seealso::
        The `W3C following definition:
        `5.4 Following Collection <https://www.w3.org/TR/activitypub/#following>`_
    """

    # renderer_classes = [JsonLDRenderer, renderers.JSONRenderer, renderers.TemplateHTMLRenderer]
    queryset = Profile.objects.all()
    lookup_field = "slug"

    paginate_by = 20
    model = Profile
    template_name = "activitypub/following.html"

    def follows(self):
        return self.get_object().actor.follows.all()

    def get(self, request, *args, **kwargs):
        result = {
            "id": self.get_object().actor.following,
            "type": "Collection",
            "totalItems": 0,
            "items": [],
        }
        follows = self.follows().values_list("id", flat=True)  # .order_by("-created")
        result.update({"totalItems": len(follows)})
        result.update({"items": json.dumps(list(follows), cls=UUIDEncoder)})
        return Response(result)
