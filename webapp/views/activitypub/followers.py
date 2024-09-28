from django.shortcuts import get_object_or_404
from django.http import JsonResponse
# from django.views.generic import DetailView

# from django.views import View
# from django.views.generic.list import MultipleObjectMixin

# from django.views.generic.detail import SingleObjectMixin
from webapp.models import Profile
# from django.contrib.sites.models import Site
from rest_framework.views import APIView
from rest_framework import renderers


class JsonLDRenderer(renderers.BaseRenderer):
    media_type = "application/activity+json"
    format = "jsonld"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


# class FollowersView(MultipleObjectMixin, DetailView):
class FollowersView(APIView):
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

    renderer_classes = [JsonLDRenderer]
    template_name = "activitypub/followers.html"
    paginate_by = 20
    model = Profile

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, slug=self.kwargs["slug"])

    def get_queryset(self):
        return self.get_object().actor.followed_by.all()

    def to_jsonld(self):
        actor = self.get_object().actor
        followers = self.get_queryset().values_list(
            "actor", flat=True
        )  # .order_by("-followed_by__created")
        wrap = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"{actor.followers}",
            "type": "OrderedCollection",
            "totalItems": len(followers),
            "items": [f"{actor.id}" for item in followers],
        }
        return wrap

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        if request.accepts("application/json") or request.accepts(
            "application/activity+json"
        ):
            return JsonResponse(
                self.to_jsonld(),
                content_type="application/activity+json",
            )
        else:
            return super().get(request, *args, **kwargs)
