from django import forms
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView
from webapp.models import Profile as Fllwng
from webapp.models import Actor

class FollowForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ["self", "following"]
        widgets = {
            "object": forms.URLInput(attrs={"class": "form-control"}),
        }

class FollowingCreateView(CreateView):
    model = Fllwng
    form_class = FollowForm

class FollowingDetailView(DetailView):
    model = Fllwng

class FollowingListView(ListView):
    model = Fllwng

class FollowingDeleteView(DeleteView):
    model = Fllwng
    success_url = "/following/"
