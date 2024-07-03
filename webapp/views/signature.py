from django.http import HttpResponse
from django.views import View


class SignatureView(View):
    def get(self, request):
        """
        Debug View for signature validation
        """
        from webapp.signature import SignatureChecker

        signature = SignatureChecker().validate(request)
        return HttpResponse(signature)
