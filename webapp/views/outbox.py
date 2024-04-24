from django.http import JsonResponse
from django.views import View

from webapp.models import Profile, Action


class OutboxView(View):
    """
    5.1 Outbox
    The outbox is a list of all activities that an actor has published. The
    outbox is a collection of activities. The outbox is ordered by the
    published property of each activity, from the most recently published
    to the oldest published. The outbox is paginated, with the most recent
    items first. The outbox is a subtype of OrderedCollection.

    https://www.w3.org/TR/activitypub/#outbox
    """

    def get(self, request, *args, **kwargs):
        # Retrieve the activity stream of the authenticated user's actor
        # ...
        from django.core.paginator import Paginator

        slug = kwargs.get("slug")
        page = request.GET.get("page", None)

        try:
            profile = Profile.objects.get(slug=slug)  # pylint: disable=E1101
        except Profile.DoesNotExist:
            return JsonResponse({"error": "Profile not found"}, status=404)

        activity_list = Action.objects.filter(actor_object_id=profile.id)
        paginator = Paginator(activity_list, 10)
        # from django.core import serializers

        # Prepare the activity stream response
        activity_stream = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollection",
            "totalItems": paginator.count,
            "first": f"{profile.get_outbox_url}?page=1",
            "last": f"{profile.get_outbox_url}?page={paginator.num_pages}",
        }

        if page:
            # Add the serialized activity list to the activity stream
            data = {}  # serializers.serialize(
            # "json",
            # paginator.page(int(page)),
            # fields=["id", "content", "published"],  # pylint: disable=E501
            # )
            activity_stream[
                "current"
            ] = f"{profile.get_outbox_url}?page={page}"  # pylint: disable=E501
            activity_stream["orderedItems"] = data

        # Return the activity stream as a JSON response
        return JsonResponse(activity_stream)
