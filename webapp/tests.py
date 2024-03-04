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

    def test_delete_message_with_activityserializer(self):
        from .serializers import ActivitySerializer

        message = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": "https://mastodon.social/users/OfficialLondonRP_#delete",
            "type": "Delete",
            "actor": "https://mastodon.social/users/OfficialLondonRP_",  # noqa: E501
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "object": "https://mastodon.social/users/OfficialLondonRP_",
            "signature": {
                "type": "RsaSignature2017",
                "creator": "https://mastodon.social/users/OfficialLondonRP_#main-key",  # noqa: E501
                "created": "2024-03-02T21:48:00Z",
                "signatureValue": "YNR3WNfmU47Y+85cLNexTLy/gUz3iyBqkNWtfyrcJNKRUu258Sn0uBve/bfC4cTGGaZEx6CHmxM8qd4QjRNWR7HmwPVgHCZeFxrFD1aWUxT9XAth80Q8I38CegDgK61EVh9+8ZFigaTYinAW4UisjSnC//vWhQJJazq+Dw1TVNmHU/YMyAbyyQ8FShWB3LMJ9Fq6HCs5lGy20hx36G3ieaA+e/YN/65jklMT1ZwJ5sihP00iZjjXMnkZI8nK83hcunCEufmDdxBOCILq/hEOC5YWJHJWp5pzyozc5QgVYeV2G4w3cEgEhKbgCW4IJuToTpD0KBoZo9zy1MqER5VYUg==",  # noqa: E501
            },
        }

        serializer = ActivitySerializer(data=message)
        result = serializer.is_valid()
        if result is False:
            print(f"result: {serializer.errors}")
        self.assertFalse(result)
