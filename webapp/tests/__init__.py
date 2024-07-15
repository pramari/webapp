import logging

from django.contrib.sites.models import Site
from django.test import Client, TestCase

from webapp.tests.activity import ActionTest
from webapp.tests.activitypub import ActivityPubTest
from webapp.tests.following import FollowingTest
from webapp.tests.inbox import InboxTest
from webapp.tests.outbox import OutboxTest
from webapp.tests.webfinger import WebfingerTests

# from webapp.tests.signature import SignatureTest

logger = logging.getLogger(__name__)

__all__ = [
    "ActionTest",
    "ActivityPubTest",
    "InboxTest",
    "OutboxTest",
    "FollowingTest",
    "WebfingerTests",
    # "SignatureTest",
    "ActivityStreamsTest",
]


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
