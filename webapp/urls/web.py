from django.urls import path
from webapp.views.web import FollowingListView

urlpatterns = [
    path(r'', FollowingListView.as_view(), name='following_list'),
]
