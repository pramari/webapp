from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from webapp.models import Like
from django import forms
import logging

logger = logging.getLogger(__name__)


class LikesForm(forms.ModelForm):
    class Meta:
        model = Like
        fields = ["actor", "object"]
        widgets = {
            "likes": forms.URLInput(attrs={"class": "form-control"}),
        }


class LikeCreateView(CreateView):
    template_name = "activitypub/like_create.html"
    form_class = LikesForm
    model = Like
    # success_url = "/thanks/"

    def get_initial(self):
        actor = self.request.user.profile_set.get().actor
        return {"actor": actor}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slug"] = self.request.user.profile_set.get().slug
        return context

    def form_valid(self, form):
        from webapp.tasks.activitypub import sendLike
        from webapp.signals import action

        action.send(
            sender=self.request.user.profile_set.get().actor,
            verb="liked",
            object=self.object,
        )
        sendLike.delay(self.request.user.profile_set.get().actor.id, object)
        return super().form_valid(form)


class LikeDetailView(DetailView):
    model = Like
    template_name = "activitypub/like_detail.html"


class LikeDeleteView(DeleteView):
    model = Like
    template_name = "activitypub/like_delete.html"
    success_url = "/thanks/"


class LikeListView(ListView):
    model = Like
    template_name = "activitypub/like_list.html"
    context_object_name = "likes"
    paginate_by = 10

    def get_queryset(self):
        from webapp.models import Profile

        slug = self.kwargs.get("slug")
        actor = Profile.objects.get(slug=slug).actor
        return Like.objects.all().order_by("-created_at").filter(actor=actor)
