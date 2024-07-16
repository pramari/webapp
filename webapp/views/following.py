# from django.views.generic import ListView
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse

from django.http import JsonResponse
from webapp.models import Actor

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
    model = Actor

    def get_queryset(self):
        return self.object.follows()

    def to_jsonld(self, *args, **kwargs):  # actor, follows):

        result = [p.id for p in selfxxxx.objectall()]
        print(f"result: {result}")
        return result

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        if (
            "Accept" in request.headers
            and "application/activity+json"
            in request.headers.get("Accept")  # noqa: E501
        ):
            jsonld = (self.to_jsonld(request, *args, **kwargs),)
            print(f"jsonld: {jsonld}")
            print(f"jsonld: {type(jsonld)}")
            return JsonResponse(
                jsonld,
                content_type="application/activity+json",
            )
        # return super().get(request, *args, **kwargs)
        return HttpResponse("Not Acceptable", status=406)
