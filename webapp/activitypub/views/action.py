from webapp.activitypub.models import Action
from webapp.activitypub.views.activity import ActivityBaseView
from webapp.activitypub.serializers import ActionSerializer
from rest_framework import response, status

class ActionView(ActivityBaseView):
    """
    Boilerplate for ActivityPub Actions view.

    "who did what to whom"

    .. seealso::
        :py:mod:webapp.urls.activitypub
        `/action/<uuid:uuid>/`
    """

    model = Action
    template_name = "activitypub/action.html"
    serializer_class = ActionSerializer

    def get_object(self):
        return Action.objects.get(pk=self.kwargs['pk'])


    def get(self, request, *args, **kwargs):
        object = self.get_object()
        if request.accepted_renderer.format == "html":
            data = {"object": object}
            return response.Response(data, template_name=self.template_name, content_type="text/html")

        data = self.serializer_class(instance=object).data
        return response.Response(data, content_type='application/activity+json', status=status.HTTP_200_OK) # ; profile="https://www.w3.org/ns/activitystreams"')
