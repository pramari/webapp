from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model

import json
import logging

logger = logging.getLogger(__name__)


class InboxTest(TestCase):
    def setUp(self):
        from webapp.models import Profile

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

    def test_inbox(self):
        response = self.client.get("/inbox/")
        self.assertEqual(response.status_code, 404)

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

    def test_random(self):
        """
        Post some data. Unrelated to ActivityPub.

        .. todo::
            Randomize the dict with keywords
            from ActivityPub and others.
        """
        from webapp.exceptions import ParseActivityError

        data = json.dumps({"bar": "baz"})
        self.client.post(
            "/accounts/andreas/inbox",
            data,
            content_type="application/json",
        )
        self.assertRaises(ParseActivityError)
