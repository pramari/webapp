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
