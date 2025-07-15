from webapp.activitypub.models import Actor
from webapp.activitypub.renderers import JsonLDRenderer, ActivityRenderer
from webapp.activitypub.serializers.actor import ActorSerializer
from webapp.activitypub.parsers import ActivityParser
from rest_framework import parsers
from django.http import Http404

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer

class ActivityBaseView(APIView):
    model = Actor
    queryset = Actor.objects.all()
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    serializer_class = ActorSerializer
    template_name = None
    parser_classes = [
        parsers.JSONParser,
        parsers.FormParser,
        parsers.MultiPartParser,
        ActivityParser
        # parsers.FileUploadParser,
    ]
    renderer_classes = [
        JsonLDRenderer,
        ActivityRenderer,
        TemplateHTMLRenderer,
    ]

    def get_object(self):
        try:
            return self.queryset.get(profile__slug=self.kwargs["slug"])
        except Actor.DoesNotExist:
            raise Http404("Actor not found")

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """
        Process the incoming message.

        No CSRF token required for incoming activities.
        """
        return super().dispatch(*args, **kwargs)
