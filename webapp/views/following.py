from django.shortcuts import get_object_or_404
from django.views.generic import ListView
# from django.http import JsonResponse
from webapp.models import Actor
from webapp.mixins import JsonLDMixin
from django.contrib.sites.models import Site

context = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "OrderedCollection",
    "totalItems": 0,
}


class FollowingView(JsonLDMixin, ListView):
    template_name = "activitypub/following.html"
    paginate_by = 10

    def to_jsonld(self, actor, follows):

        base = f"https://{Site.objects.get_current().domain}"
        context.update({"id": f"{base}{actor.get_following_url}"})
        context.update({"totalItems": len(follows)})
        if not len(follows):
            context.update({"first": f"{base}{actor.get_following_url}?page=0"})  # noqa: E501
        else:
            context.update(
                {"items": [f"{base}{item.get_actor_url}," for item in follows]}
            )
        return context

    def get_queryset(self):
        base = f"https://{Site.objects.get_current().domain}"
        username = self.kwargs["slug"]
        actor_id = f"{base}/@{username}"
        actor = get_object_or_404(Actor, id=actor_id)
        return actor.follows.all()
        # .filter(consent=True)
        # .filter(user__is_verified=True)
