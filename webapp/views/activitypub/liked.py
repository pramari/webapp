import json

# from django.views.generic.detail import DetailView
# from django.http import JsonResponse
from rest_framework.response import Response
from webapp.models import Profile

from rest_framework import generics
from rest_framework import renderers
from webapp.renderers import JsonLDRenderer


class LikedView(generics.RetrieveAPIView):
    """
    View for handling the objects an actor liked.

    ```
    GET /liked/
    ```

    Every actor MAY have a liked collection. This is a list of every object
    from all of the actor's Like activities, added as a side effect. The
    liked collection MUST be either an OrderedCollection or a Collection
    and MAY be filtered on privileges of an authenticated user or as
    appropriate when no authentication is given.

    .. seealso::
        `ActivityPub Liked <https://www.w3.org/TR/activitypub/#liked>`_
    """

    renderer_classes = [JsonLDRenderer, renderers.JSONRenderer]
    queryset = Profile.objects.all()
    lookup_field = "slug"
    model = Profile

    def liked(self):
        result = self.get_object().actor.like_set.all()
        return result

    def get(self, request, *args, **kwargs):
        result = {
            "id": f"{self.get_object().actor.liked}",
            "type": "Collection",
            "totalItems": 0,
            "items": [],
        }
        likes = self.liked().values_list("object", flat=True).order_by("-created_at")
        result.update({"totalItems": len(likes)})
        result.update({"items": json.dumps(list(likes))})
        # return JsonResponse(result, content_type="application/activity+json")
        # self.object = self.get_object()
        return Response(result)
