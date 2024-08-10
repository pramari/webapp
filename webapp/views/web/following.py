from django import forms
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView
# from webapp.models import Profile as Fllwng
from webapp.models import Actor

class FollowForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = "__all__"
        widgets = {
            "object": forms.URLInput(attrs={"class": "form-control"}),
        }

class FollowingCreateView(CreateView):
    model = Actor
    form_class = FollowForm

class FollowingDetailView(DetailView):
    model = Actor

class FollowingListView(ListView):
    model = Actor

class FollowingDeleteView(DeleteView):
    model = Actor
    success_url = "/following/"
