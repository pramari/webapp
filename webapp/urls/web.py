from django.urls import path
from webapp.views.web import (
    LikeListView,
    LikeCreateView,
    LikeDetailView,
    LikeDeleteView,
)
from webapp.views.web import (
    FollowingListView,
    FollowingCreateView,
    FollowingDetailView,
    FollowingDeleteView,
)
from webapp.views.signature import SignatureView

urlpatterns = [
    path(r"like/", LikeCreateView.as_view(), name="like-create"),
    path(r"like/<slug:slug>/list", LikeListView.as_view(), name="like-list"),
    path(r"like/<uuid:pk>", LikeDetailView.as_view(), name="like-detail"),
    path(
        r"like/<uuid:pk>/delete", LikeDeleteView.as_view(), name="like-delete"
    ),  # noqa: E501
]

urlpatterns += [
    path(r"follow/", FollowingCreateView.as_view(), name="follow-create"),
    path(r"follow/list", FollowingListView.as_view(), name="follow-list"),
    path(
        r"follow/<uuid:pk>", FollowingDetailView.as_view(), name="follow-detail"
    ),
    path(
        r"follow/<uuid:pk>/delete",
        FollowingDeleteView.as_view(),
        name="follow-delete",
    ),
]

urlpatterns += [
    # Debug view to show the signature of a given object
    path(r"signature", SignatureView.as_view(), name="signature"),
]
