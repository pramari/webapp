from django.test import TestCase


class ActionTest(TestCase):
    def setUp(self):
        """
        Setup test.
        """

    def test_note(self):
        """
        Create a note.

        Validate that the note is created, a
        signal is sent, and action is created.
        """
        from webapp.models import Note, Action
        from django.dispatch import Signal

        note_create = Signal()

        n = Note.objects.create(content="Hello, World!")
        n.save()

        note_create.send(
            sender="webapp.models.Note", instance=n, verb="Create"
        )  # noqa: E501

        self.assertTrue(isinstance(n, Note))
        self.assertGreater(Action.objects.count(), 0)

    def test_actor_model(self):
        from webapp.models import Profile, Action

        p = Profile.objects.get(pk=1)
        Action.objects.actor(p)
