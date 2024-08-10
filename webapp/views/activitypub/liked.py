from django.views.generic.detail import DetailView
from django.http import JsonResponse
from webapp.models import Profile


class LikedView(DetailView):
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

    models = Profile

    def liked(self):
        return self.get_object().actor.liked.all()

    def get(self, request, *args, **kwargs):
        result = {"type": "Collection", "totalItems": 0, "items": []}
        return JsonResponse(result, contenttype="application/activity+json")
