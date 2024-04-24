from django.views.generic import ListView

from webapp.models import Profile


class FollowingView(ListView):
    template_name = "activitypub/following.html"

    def get_queryset(self):
        from django.shortcuts import get_object_or_404

        profile = get_object_or_404(Profile, slug=self.kwargs["slug"])
        return profile.follows.filter(consent=True)
        # .filter(user__is_verified=True)
