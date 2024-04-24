import json
import logging
from django.test import TestCase
from django.test import Client
from django.contrib.sites.models import Site

logger = logging.getLogger(__name__)


class ToolTest(TestCase):
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
        from .activity import getRemoteActor

        result = getRemoteActor("https://pramari.de/accounts/andreas/actor/")

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
        from .models import Note, Action
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


class ActivityTest(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from .models import Profile

        self.client = Client()  # A client for all tests.

        User = get_user_model()

        user = User.objects.create_user(
            username="andreas",
            email="andreas@neumeier.org",
            password="top_secret",  # noqa: E501
        )
        user.save()
        profile = Profile.objects.get(user=user)
        self.assertTrue(isinstance(profile, Profile))

    def test_random(self):
        """
        Post some data. Unrelated to ActivityPub.

        .. todo::
            Randomize the dict with keywords from ActivityPub and others.
        """
        from .exceptions import ParseActivityError

        data = json.dumps({"bar": "baz"})
        self.client.post(
            "/accounts/andreas/inbox",
            data,
            content_type="application/json",
        )
        self.assertRaises(ParseActivityError)

    def test_follow(self):
        """
        Post a follow activity.
        """
        with open(
            "submodules/taktivitypub/tests/data/follow-mastodon.json"
        ) as f:  # noqa: E501
            data = f.read()
            self.client.post(
                "/accounts/andreas/inbox",
                data,
                content_type="application/json",
            )

    def test_outbox(self):
        """
        Test whether the outbox is reachable.
        """
        result = self.client.get(
            "/accounts/andreas/outbox",
        )
        logger.debug(f"result: {result.content}")
        self.assertEqual(result.status_code, 200)

    def test_outbox_content(self):
        """
        Test whether the outbox is reachable.
        This time when the outbox is not empty.
        """
        from .models import Note
        from django.contrib.auth import get_user_model
        from django.dispatch import Signal

        User = get_user_model()

        n = Note.objects.create(content="Hello, World!")
        n.save()
        u = User.objects.get(username="andreas")
        Signal().send(sender=Note, instance=n, actor=u, verb="Create")
        result = self.client.get(
            "/accounts/andreas/outbox",
        )
        logger.debug(f"result: {result.content}")
        self.assertEqual(result.status_code, 200)
