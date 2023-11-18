import json
# from django.views import View
# from django.http import JsonResponse
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from rest_framework import views, status, response, permissions
from .serializers import BudgetSerializer

import logging

logger = logging.getLogger(__name__)


class BudgetView(views.APIView):
    """
    BudgetView.

    Receive Budget from `GCP PubSub`.
    """

    queryset = get_user_model().objects.all()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, bundle=None, format=None):  # pylint: disable=R0201
        """POST method."""
        logger.debug("POST %s", request.data)
        serializer = BudgetSerializer(data=request.data)
        if serializer.is_valid():
            import base64

            budget = base64.b64decode(
                serializer.validated_data["message"]["data"]
            )
            logger.info(
                "Subscription: %s", serializer.validated_data["subscription"]
            )
            jsonBudget = json.loads(budget)
            """
            # logger.info("Keys: %s" % .keys())
            # Keys: dict_keys([
                'budgetDisplayName', 'costAmount',
                'costIntervalStart', 'budgetAmount',
                'budgetAmountType', 'currencyCode']
                )
            """
            logger.info(
                "Budget %s: %s (%s)",
                jsonBudget['budgetDisplayName'],
                jsonBudget["costAmount"],
                jsonBudget["budgetAmount"]
            )
            # serializer.save()
        else:
            logger.debug("Invalid: %s", serializer.data)
        #    return Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response("OK!", status=status.HTTP_201_CREATED)
