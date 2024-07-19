from django.views.generic import View
from django.views.generic.list import MultipleObjectMixin
from django.http import HttpResponse


class LikesView(MultipleObjectMixin, View):

    def get(self, request, *args, **kwargs):
        # Do something
        return HttpResponse("GET request")
