"""
See: `:py:class:`GlobalInboxView` <webapp.activitypub.views.globalinbox.GlobalInboxView>`
"""

from .activity import ActivityBaseView
from rest_framework.response import Response
from rest_framework import status

class GlobalInboxView(ActivityBaseView):
    def post(self, request):
        # Implement the logic to handle incoming ActivityPub activities
        return Response({"status": "success"}, status=status.HTTP_200_OK)
