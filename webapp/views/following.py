from django.shortcuts import get_object_or_404

# from django.views.generic import ListView
from django.views.generic import View
from django.http import HttpResponse

from django.http import JsonResponse
from webapp.models import Profile

# from django.contrib.sites.models import Site

context = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "OrderedCollection",
    "totalItems": 0,
}


class FollowingView(View):
    template_name = "activitypub/following.html"
    paginate_by = 10

    def get(self, request, *args, **kwargs):  # pylint: disable=W0613
        if (
            "Accept" in request.headers
            and "application/activity+json"
            in request.headers.get("Accept")  # noqa: E501
        ):
            jsonld = self.to_jsonld(request, *args, **kwargs),
            return JsonResponse(
                jsonld,
                content_type="application/activity+json",
            )
        # return super().get(request, *args, **kwargs)
        return HttpResponse("Not Acceptable", status=406)

    def to_jsonld(self, *args, **kwargs):  # actor, follows):
        slug = kwargs.get("slug")
        profile = get_object_or_404(Profile, user__username=slug)

        print(f"slug: {slug}")
        print(f"profile: {profile}")
        print(f"actor: {profile.actor}")

        username = self.kwargs["slug"]
        profile = get_object_or_404(Profile, user__username=username)
        result = {p.id for p in profile.actor.follows.all()}
        print(f"result: {result}")
        return result

        # base = f"https://{Site.objects.get_current().domain}"
        # context.update({"id": f"{base}{actor.get_following_url}"})
        # context.update({"totalItems": len(follows)})
        # if not len(follows):
        #     context.update({"first": f"{base}{actor.get_following_url}?page=0"})  # noqa: E501
        # else:
        #     context.update(
        #         {"items": [f"{base}{item.get_actor_url}," for item in follows]}  # noqa: E501
        #     )
        return {}
