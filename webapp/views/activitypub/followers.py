from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.http import JsonResponse

from webapp.models import Profile
from django.contrib.sites.models import Site


class FollowersView(DetailView):
    """
    Provide a list of followers for a given profile.


    .. note::
        The reverse for this view is `actor-followers`.
        The URL pattern `/accounts/<slug:slug>/followers/`

    .. seealso::
        The `W3C followers definition <https://www.w3.org/TR/activitystreams-vocabulary/#followers>`_.  # noqa
    """

    template_name = "activitypub/followers.html"
    model = Profile

    def followers(self):
        return self.get_object().actor.followed_by.all()

    def to_jsonld(self, *args, **kwargs):
        actor = self.get_object().actor
        base = f"https://{Site.objects.get_current().domain}"
        followers = self.followers().values_list("actor", flat=True).order_by("-created")
        wrap = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"https://{base}{actor.followers_url}",
            "type": "OrderedCollection",
            "totalItems": len(self.followers),
            "items": [f"{item.id}" for item in followers],
        }
        return wrap

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        if request.accepts("application/json") or request.accepts(
            "application/activity+json"
        ):
            profile = get_object_or_404(Profile, slug=self.kwargs["slug"])
            return JsonResponse(
                self.to_jsonld(profile, self.get_queryset()),
                content_type="application/activity+json",
            )
        else:
            return super().get(request, *args, **kwargs)
