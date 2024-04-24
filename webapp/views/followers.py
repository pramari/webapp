from django.views.generic import ListView

from webapp.models import Profile


class FollowersView(ListView):
    """
    Provide a list of followers for a given profile.

    .. url:: /accounts/<slug:slug>/followers/
    """

    template_name = "activitypub/followers.html"

    def get_queryset(self):
        from django.shortcuts import get_object_or_404

        profile = get_object_or_404(Profile, slug=self.kwargs["slug"])
        return profile.followed_by.filter(consent=True)
        # .filter(user__is_verified=True)
