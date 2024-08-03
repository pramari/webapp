# from django.views.generic import ListView
from django.views.generic.list import ListView
from django.http import HttpResponse

from django.http import JsonResponse
from webapp.models import Profile

# from django.contrib.sites.models import Site

orderedCollection = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "OrderedCollection",
    "id": "https://23.social/users/andreasofthings/following",
    "totalItems": 371,
    "first": "https://23.social/users/andreasofthings/following?page=1",
}


"""
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "https://23.social/users/andreasofthings/following?page=1",
  "type": "OrderedCollectionPage",
  "totalItems": 371,
  "next": "https://23.social/users/andreasofthings/following?page=2",
  "partOf": "https://23.social/users/andreasofthings/following",
  "orderedItems": [
    "..."
  ]
}
"""


context = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "OrderedCollection",
    "totalItems": 0,
}


class FollowingView(ListView):
    template_name = "activitypub/following.html"
    paginate_by = 10
    model = Profile

    def get_queryset(self):
        return Profile.objects.filter(slug=self.kwargs["slug"])  # noqa: E501

    def jsonld(self, request, *args, **kwargs):
        page = request.GET.get("page", None)
        actor = self.get_queryset().get().actor
        totalItems = actor.follows.count()  # noqa: F841

        orderedCollection.update({"totalItems": totalItems})
        if not page:
            orderedCollection.update({"first": f"{actor.id}/following?page=1"})
        if totalItems > 10:
            orderedCollection.update({"next": f"{actor.id}/following?page=2"})

        return JsonResponse(
            orderedCollection,
            content_type="application/activity+json",
        )

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        if (
            "Accept" in request.headers
            and "application/activity+json"
            in request.headers.get("Accept")  # noqa: E501
        ):
            return self.jsonld(request, *args, **kwargs)
        return HttpResponse("Not Acceptable", status=406)
