import json
# from django.views.generic.detail import DetailView
# from django.http import JsonResponse
from rest_framework.response import JsonResponse
from webapp.models import Profile

from rest_framework import generics
from webapp.renderers import JsonLDRenderer


    


class LikedView(generics.RetrieveAPIView):
    """
    View for handling the liked a

    ```
    GET /liked/
    ```

    Every actor MAY have a liked collection. This is a list of every object from all of the actor's Like activities, added as a side effect. The liked collection MUST be either an OrderedCollection or a Collection and MAY be filtered on privileges of an authenticated user or as appropriate when no authentication is given.

    .. seealso::
        `ActivityPub Liked <https://www.w3.org/TR/activitypub/#liked>`_

    .. seealso:: :class:`django.views.generic.View`

    .. seealso::
        :class:`django.http.HttpResponse`
    """
    renderer_classes = [JsonLDRenderer]
    queryset = Profile.objects.all()

    model = Profile

    def liked(self):
        result = self.get_object().actor.like_set.all()
        return result

    def get(self, request, *args, **kwargs):
        result = {"type": "Collection", "totalItems": 0, "items": []}
        likes = self.liked().values_list("object", flat=True).order_by("-created_at")
        result.update({"totalItems": len(likes)})
        result.update({"items": json.dumps(list(likes))})
        # return JsonResponse(result, content_type="application/activity+json")
        self.object = self.get_object()
        return JsonResponse({'user': self.object}, template_name='user_detail.html')
