from webapp.api_views import BudgetView

from rest_framework import (
    views, routers, serializers, viewsets, permissions, response
)
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
    required_scopes = ['userinfo']
    serializer_class = UserSerializer


    def get(self, request, *args, **kwargs):
        userinfo = User.objects.get(pk=self.request.user.pk)
        return response.Response(UserSerializer(userinfo).data)


router = routers.DefaultRouter()
router.register(r"user", UserViewSet, basename="user")

urlpatterns = [
    path(r"api/userinfo/", UserDetails.as_view()),
    path(r"api/", include(router.urls)),
]

urlpatterns += [
    path("pubsub/push/", BudgetView.as_view()),
]
