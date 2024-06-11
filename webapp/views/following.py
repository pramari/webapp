from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.http import JsonResponse
from webapp.models import Profile
from django.contrib.sites.models import Site


class FollowingView(ListView):
    template_name = "activitypub/following.html"

    def to_jsonld(self, actor, follows):
        base = f"https://{Site.objects.get_current().domain}"
        wrap = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"{base}{actor.get_following_url}",
            "summary": f"{actor}'s is following",
            "type": "OrderedCollection",
            "totalItems": len(follows),
            "items": [f"{item.get_actor_url}," for item in follows],
        }
        return wrap

    def get_queryset(self):
        profile = get_object_or_404(Profile, slug=self.kwargs["slug"])
        return profile.follows.all()
        # .filter(consent=True)
        # .filter(user__is_verified=True)

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        if (
            "Accept" in request.headers
            and "application/activity+json" in request.headers.get("Accept")
        ):
            profile = get_object_or_404(Profile, slug=self.kwargs["slug"])
            return JsonResponse(
                self.to_jsonld(profile, self.get_queryset()),
                content_type="application/activity+json",
            )
        else:
            return super().get(request, *args, **kwargs)
