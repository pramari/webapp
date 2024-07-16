# from django.views.generic import ListView
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse

from django.http import JsonResponse
from webapp.models import Profile

# from django.contrib.sites.models import Site

"""
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "https://23.social/users/andreasofthings/following",
  "type": "OrderedCollection",
  "totalItems": 371,
  "first": "https://23.social/users/andreasofthings/following?page=1"
}
"""

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


class FollowingView(SingleObjectMixin, View):
    template_name = "activitypub/following.html"
    paginate_by = 10
    model = Profile

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        actor = self.get_object().actor_set.get()
        totalItems = self.get_object().actor_set.get().following.count() # noqa: E501, F841
        orderedItems = [p.id for p in self.get_object().actor_set.get().following.all()]  # noqa: E501, F841

        if (
            "Accept" in request.headers
            and "application/activity+json"
            in request.headers.get("Accept")  # noqa: E501
        ):
            jsonld = context
            jsonld["id"] = f"{actor.id}/following"
            jsonld["totalItems"] = totalItems
            jsonld["first"] = f"{actor.id}/following?page=1"
            jsonld["orderedItems"] = orderedItems

            print(f"jsonld: {jsonld}")
            print(f"jsonld: {type(jsonld)}")
            return JsonResponse(
                jsonld,
                content_type="application/activity+json",
            )
        # return super().get(request, *args, **kwargs)
        return HttpResponse("Not Acceptable", status=406)
