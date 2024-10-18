import logging

from rest_framework import generics
from rest_framework.response import Response
from webapp.models import Profile  # Profile is hosting Actor
from webapp.serializers.actor import ActorSerializer

logger = logging.getLogger(__name__)


class ActorView(generics.GenericAPIView):
    """
    Return the actor object for a given user.
    User is identified by the slug.

    :py:class:`webapp.models.activitypub.Actor` is the model that hosts the actor object.

    Example urlconf:
        ```
        path(
        r'@<slug:slug>',
        ActorView.as_view(),
        name='actor-view')
        ```

    If the request header contains 'application/activity+json',
    the response will be in Activity Streams 2.0 JSON-LD format.
    Otherwise, the response will redirect the client to the `profile-page`.

    The actor object is a JSON-LD object that represents the user.

    .. seealso::
        `W3C Actor Objects <https://www.w3.org/TR/activitypub/#actor-objects>`_

    .. seealso::
        :py:mod:`webapp.urls.activitypub`

    """

    redirect_to = "profile-detail"
    serializer_class = ActorSerializer
    queryset = Profile.objects.all()  # todo: local profiles, approved profiles
    lookup_field = "slug"
    model = Profile
    template_name = "activitypub/actor.html"

    def get_object(self):
        """
        Search for the profile, return the actor.
        """
        return self.queryset.get(slug=self.kwargs["slug"]).actor

    def get(self, request, *args, **kwargs):
        logger.debug(
            "ActorView.get(): acceppted media types: %s", request.accepted_media_type
        )
        if request.accepted_renderer.format == "html":
            data = {"actor": self.get_object()}
            return Response(data, template_name=self.template_name)
        actor = self.serializer_class(instance=self.get_object()).data
        return Response(actor)
