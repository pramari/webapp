from django.test import TestCase


class ActionTest(TestCase):
    def setUp(self):
        """
        Setup test.
        """
        from webapp.models import Actor, Note

        self.id = "https://test.com/@Test"
        self.a = Actor.objects.create(id=self.id)
        self.n = Note.objects.create(content="Hello, World!")

    def test_signal(self):
        """
        Action Signal Test.

        Validate that the signal actually created an Action object.
        """
        from webapp.models import Action
        from webapp.signals import action

        a = action.send(
            sender=self.a,  # "webapp.models.Actor",
            verb="Create",
            # action_object=self.n,
            target=self.n,
        )  # noqa: E501

        for f, r in a:
            self.assertTrue(isinstance(r, Action))

        self.assertEqual(Action.objects.count(), 1)

    def test_actor_model(self):
        from webapp.models import Action, Actor

        p = Actor.objects.get(id=self.id)
        Action.objects.actor(p)
