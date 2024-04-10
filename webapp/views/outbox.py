from django.http import JsonResponse
from django.views import View
from ..models import Profile


class OutboxView(View):
    """ """

    def get(self, request, *args, **kwargs):
        # Retrieve the activity stream of the authenticated user's actor
        # ...

        slug = kwargs.get("slug")

        profile = Profile.objects.get(slug=slug)  # pylint: disable=E1101

        activity_list = profile.activities

        # Prepare the activity stream response
        activity_stream = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollection",
            "totalItems": len(activity_list),
            "orderedItems": activity_list,
        }

        # Return the activity stream as a JSON response
        return JsonResponse(activity_stream)
