from webapp.api_views import BudgetView

from rest_framework import views, routers, serializers, viewsets, permissions, response
from django.urls import path, include
from django.contrib.auth import get_user_model

from oauth2_provider.contrib.rest_framework import TokenHasScope

import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # pylint: disable=R0903
    class Meta:
        model = User
        fields = (
            "pk",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_verified",
            # "dob",
            "public",
            "consent",
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    # Users API.

    List and Manage `Users` registered to :url:www.pramari.de.

    Terms and conditions apply here.
    """

    basename = "user"  # User.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
    ]  # , TokenHasScope]
    required_scopes = ["read"]
    serializer_class = UserSerializer

    def get_queryset(self):
        """Overwrite get_queryset() from ModelViewSet."""
        logger.debug("get_queryset for user PK: %s", self.request.user)
        return User.objects.filter(pk=self.request.user.pk)


class UserDetails(views.APIView):
    # authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ["userinfo"]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        userinfo = User.objects.get(pk=self.request.user.pk)
        return response.Response(UserSerializer(userinfo).data)


class EventView(views.APIView):
    """
    POST <QueryDict: {'
    {
        "messageMetadata":{
            "accessToken":"ADMQFHJwiPCZc-vc2mdDUDEprZmQfkaWRnwYNfHhp9BJNqL3pIoMLEXFO8xS-xq-nTtHuuK6ETqmfSIqR7pJ_EESCAwQvQ4179OpAbCiDZSvXmxRXzMDo2ldkpadrF2sAysVfxzqDPV-RkxLJHW5CnDduvYXgbbA1A",
            "threadId":"thread-f:1785020815841123550",
            "messageId":"msg-f:1785020815841123550"
        },
        "hostApp":"gmail",
        "gmail":{
            "messageId":"msg-f:1785020815841123550",
            "accessToken":"ADMQFHKfopKsGpiYPekskSnIWNg2CnNkSQk_czJmESmff_ARw0b2g_WTcS74q-0FembMWPXVQ2OqNZtL5KFmZBwaDqEZSCnMraibGusW9rnLhCcMk2hquxOfv1M9ykJKOxhAvVD7sQVCqeoOT19fkDTMR80-v4b0rg",
            "threadId":"thread-f:1785020815841123550"
        },
        "commonEventObject":{
            "hostApp":"GMAIL",
            "platform":"WEB"
        },
        "clientPlatform":"web"
        }': ['']
    }>
    """
    queryset = get_user_model().objects.all()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, bundle=None, format=None):  # pylint: disable=R0201
        from rest_framework import status
        """POST method."""
        logger.error("POST %s", ", \n".join(request.data.items()))
        return response.Response("OK!", status=status.HTTP_200_OK)


router = routers.DefaultRouter()
router.register(r"user", UserViewSet, basename="user")

urlpatterns = [
    path(r"api/userinfo/", UserDetails.as_view()),
    path(r"api/mail/", EventView.as_view()),
    path(r"api/", include(router.urls)),
    path("pubsub/push/", BudgetView.as_view()),
]
