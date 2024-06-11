from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.http import JsonResponse

from webapp.models import Profile
from webapp.mixins import JsonLDMixin
from django.contrib.sites.models import Site


class FollowersView(JsonLDMixin, ListView):
    """
    Provide a list of followers for a given profile.

    .. url:: /accounts/<slug:slug>/followers/
    """

    template_name = "activitypub/followers.html"

    def to_jsonld(self, *args, **kwargs):
        slug = kwargs.get("slug")
        profile = get_object_or_404(Profile, slug=slug)
        followers = profile.followed_by.filter(consent=True)
        # .filter(user__is_verified=True)

        base = f"https://{Site.objects.get_current().domain}"
        wrap = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"{base}{profile.get_followers_url}",
            "summary": f"{profile}'s followers",
            "type": "OrderedCollection",
            "totalItems": len(followers),
            "items": [f"{item.get_actor_url}" for item in followers],
        }
        return wrap

    def get_queryset(self):
        from django.shortcuts import get_object_or_404

        profile = get_object_or_404(Profile, slug=self.kwargs["slug"])
        return profile.followed_by.filter(consent=True)
        # .filter(user__is_verified=True)

    def oldget(self, request, *args, **kwargs):  # pylint: disable=W0613
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
