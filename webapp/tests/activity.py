from django.test import TestCase


class ActionTest(TestCase):
    def setUp(self):
        """
        Setup test.
        """
        from webapp.models import Actor, Note

        self.a = Actor.objects.create(id="https://test.com/@Test")
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
            print(f"{f}: {r}")
            self.assertTrue(isinstance(r, Action))

        self.assertEqual(Action.objects.count(), 1)

    def test_actor_model(self):
        from webapp.models import Action, Profile

        p = Profile.objects.get(pk=1)
        Action.objects.actor(p)
