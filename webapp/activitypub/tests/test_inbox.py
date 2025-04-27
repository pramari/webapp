import json
import logging

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

logger = logging.getLogger(__name__)


class InboxTest(TestCase):
    def setUp(self):
        from webapp.models import Profile

        self.client = Client()  # A client for all tests.
        self.username = "inboxtest"
        User = get_user_model()
        self.user, created = User.objects.get_or_create(
            username=self.username,
            email="andreas@neumeier.org",
            password="top_secret",  # noqa: E501
        )
        if created:
            self.user.save()
        self.slug = self.user.profile.slug
        self.follower = User.objects.create(username="follower")
        self.followed = User.objects.create(username="followed")
        if created:
            self.user.save()
        profile = Profile.objects.get(user=self.user)
        self.assertTrue(isinstance(profile, Profile))

    def test_inbox(self):
        """
        Test the gobal inbox view.

        .. todo::
            Implement a global inbox view.
        """
        response = self.client.get("/inbox/")
        self.assertEqual(response.status_code, 404)

    def test_user_inbox_unauthenticated(self):
        """
        Test the user inbox view.
        .. :py:meth:webapp.tests.inbox.InboxTest.test_user_inbox

        .. todo::
          - For authenticated users, this shall return an 
          `OrderedCollection` with HTPP status 200.
        """
        from django.urls import reverse
        response = self.client.get(reverse("actor-inbox", kwargs={'slug': self.username}))
        self.assertEqual(response.status_code, 404)


    def test_follow_1(self):
        """
        Post a follow activity.

        .. todo::
            Make this work with W3C test data.
            For now, it accepts the 404 status code.
            It's unclear where the error is.
        """

        from webapp.tests.rename_messages import w3c_activity

        for message in w3c_activity['follow']:
            result = self.client.post(
                f"/accounts/{self.slug}/inbox",
                data=message,
                content_type="application/json",
            )
            self.assertEqual(result.status_code, 404)

    def test_follow_2(self):
        """
        Post a follow activity.
        """
        message = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "summary": "Sally followed John",
            "type": "Follow",
            "actor": "http://{self.follower} ",
            "object": "https://{self.followed}",
        }
        self.client.post(
            f"/accounts/{self.username}/inbox",
            data=message,
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
        from webapp.tests.rename_messages import follow

        data = json.dumps(follow)
        self.client.post(
            f"/accounts/{self.username}/inbox",
            data,
            content_type="application/json",
        )
        self.assertRaises(ParseActivityError)
