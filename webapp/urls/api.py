"""
webapp urls.py that define possible API invocation options.
"""

import logging
# from rest_framework import views
# from rest_framework import routers
# from rest_framework import serializers
# from rest_framework import viewsets
# from rest_framework import permissions
# from rest_framework import response

from django.urls import path # , include
# from django.contrib.auth import get_user_model

# from oauth2_provider.contrib.rest_framework import TokenHasScope

from webapp.views.api import BudgetView


logger = logging.getLogger(__name__)
# User = get_user_model()

"""
class UserSerializer(serializers.ModelSerializer):
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
            # "profile__public",
            # "consent",
            "services",
            "profile__img",
        )
"""
"""
class UserViewSet(viewsets.ModelViewSet):

    basename = "user"  # User.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
    ]  # , TokenHasScope]
    required_scopes = ["read"]
    serializer_class = UserSerializer

    def get_queryset(self):
        logger.debug("get_queryset for user PK: %s", self.request.user)
        return User.objects.filter(pk=self.request.user.pk)


class UserDetails(views.APIView):
    # authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ["userinfo"]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        userinfo = User.objects.get(pk=self.request.user.pk)
        # logger.error(UserSerializer(userinfo).data)
        return response.Response(UserSerializer(userinfo).data)
"""




# router = routers.DefaultRouter()
# router.register(r"user", UserViewSet, basename="user")

urlpatterns = [
    # path(r"api/userinfo/", UserDetails.as_view()),
    # path(r"api/", include(router.urls)),
    path("pubsub/push/", BudgetView.as_view()),
]
