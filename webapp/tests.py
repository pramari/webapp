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


class SerializerTest(TestCase):
    def setUp(self):
        pass


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


class ActivityTest(TestCase):
    def setUp(self):
        self.client = Client()

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
        with open(
            "submodules/taktivitypub/tests/data/follow-mastodon.json"
        ) as f:  # noqa: E501
            data = f.read()
            self.client.post(
                "/accounts/andreas/inbox",
                data,
                content_type="application/json",
            )
