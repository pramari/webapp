from django.test import TestCase
from django.test import Client
from webapp.tasks.activitypub import Fetch


class ActivityTest(TestCase):
    def setUp(self):
        """
        Setup test.
        """
        self.client = Client()

    def test_actvity_fetch(self):
        self.assertTrue(Fetch("https://pramari.de/@andreas"))

    def test_actvity_fetch_blocked(self):
        with self.assertRaises(ValueError):
            result = Fetch("https://blocked")  # noqa: F841

    def test_actvity_fetch_invalid(self):
        with self.assertRaises(ValueError):
            result = Fetch("example")  # noqa: F841

    def test_actvity_fetch_onion(self):
        with self.assertRaises(ValueError):
            activity = Fetch("http://example.onion")  # noqa: F841

    def test_activity_actor_remote(self):
        """
        test getRemoteActor helper function
        """
        from webapp.tasks.activitypub import getRemoteActor

        result = getRemoteActor("https://pramari.de/@andreas")

        self.assertEqual(result.get("id"), "https://pramari.de/@andreas")  # noqa: E501


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
