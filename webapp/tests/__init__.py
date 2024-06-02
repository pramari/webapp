import logging
from django.test import TestCase
from django.test import Client
from django.contrib.sites.models import Site

from webapp.tests.inbox import InboxTest
from webapp.tests.outbox import OutboxTest
from webapp.tests.following import FollowingTest
from webapp.tests.webfinger import WebfingerTests

logger = logging.getLogger(__name__)

__all__ = ["InboxTest", "OutboxTest", "FollowingTest", "WebfingerTests"]


class ToolTest(TestCase):
    """
    Test availability for tools built into the application.
    """

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_nodeinfo(self):
        # Issue a GET request.
        response = self.client.get("/.well-known/nodeinfo")
        self.assertEqual(response.status_code, 200)
        result = response.json()["links"][0]["href"]
        base = f"https://{Site.objects.get_current().domain}"
        logger.debug(f"base: {base}")
        self.assertEqual(result, "/api/v1/version")

    def test_version(self):
        # Issue a GET request.
        response = self.client.get("/api/v1/version")
        self.assertEqual(response.status_code, 200)


class TactivityTest(TestCase):
    def setUp(self):
        """
        Setup test.
        """
        self.client = Client()

    def test_actor_remote(self):
        """
        test getRemoteActor helper function
        """
        from webapp.tasks.activitypub import getRemoteActor

        result = getRemoteActor("https://pramari.de/@andreas")

        self.assertEqual(
            result.id, "https://pramari.de/accounts/andreas/actor/"
        )  # noqa: E501


class ActionTest(TestCase):
    def setUp(self):
        """
        Setup test.
        """
        self.client = Client()

    def test_note(self):
        """
        Create a note.

        Validate that the note is created, a
        signal is sent, and action is created.
        """
        from webapp.models import Note, Action
        from webapp.signals import action

        n = Note.objects.create(content="Hello, World!")
        n.save()
        self.assertTrue(isinstance(n, Note))

        action.send(sender=Note, instance=n, verb="Create")  # noqa: E501

        self.assertGreater(Action.objects.count(), 0)

    def test_actor_model(self):
        from webapp.models import Profile, Action

        p = Profile.objects.get(pk=1)
        Action.objects.actor(p)
