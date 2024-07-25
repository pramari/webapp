from django.views.generic.detail import DetailView


from webapp import contenttype

from webapp.models import Note, Action


class ActionView(DetailView):
    """
    Boilerplate for ActivityPub Actions view.

    "who did what to whom"

    .. seealso::
        :py:mod:webapp.urls.activitypub
        `/action/<uuid:uuid>/`
    """

    model = Action
    template_name = "activitypub/action.html"


class NoteView(DetailView):
    """
    Boilerplate for ActivityPub Note view.

    A Note is a short written work, typically
    less than a single paragraph in length.

    This view will return a json-ld representation
    of the note if requested.

    .. seealso::
        :py:mod:webapp.urls.activitypub
        `/action/<uuid:uuid>/`

    """

    model = Note
    template_name = "activitypub/note.html"

    def json_ld(self, request):
        from django.http import JsonResponse

        """
        Return a json-ld representation of the note.
        """
        json_ld = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Note",
            "id": self.get_object().get_absolute_url(),
            "content": self.get_object().content,
            "published": self.get_object().published.isoformat(),
            "attributedTo": self.get_object().author.get_absolute_url(),
        }

        return JsonResponse(json_ld, content_type="application/ld+json")

    def dispatch(self, request, *args, **kwargs):
        """
        Make the view return json_ld if requested.
        """
        if request.META.get("HTTP_ACCEPT") in contenttype:
            return self.json_ld(request)
        return super().dispatch(request, *args, **kwargs)
