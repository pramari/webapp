from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.http import JsonResponse
from webapp.models import Profile


class FollowersView(ListView):
    """
    Provide a list of followers for a given profile.

    .. url:: /accounts/<slug:slug>/followers/
    """

    template_name = "activitypub/followers.html"

    def to_jsonld(self, actor, followers):
        wrap = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "summary": f"{actor}'s followers",
            "type": "Collection",
            "totalItems": len(followers),
            "items": [
                {
                    "type": "Person",
                    "id": item.get_actor_url,
                    "name": item.user.username,
                }  # noqa: E501
                for item in followers
            ],
        }
        return wrap

    def get_queryset(self):
        from django.shortcuts import get_object_or_404

        profile = get_object_or_404(Profile, slug=self.kwargs["slug"])
        return profile.followed_by.filter(consent=True)
        # .filter(user__is_verified=True)

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
