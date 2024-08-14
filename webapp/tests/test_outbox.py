import logging

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

logger = logging.getLogger(__name__)


class OutboxTest(TestCase):
    def setUp(self):
        from webapp.models import Profile

        self.client = Client()  # A client for all tests.
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username="andreas",
            email="andreas@neumeier.org",
            password="top_secret",  # noqa: E501
        )
        if created:
            user.save()
        profile = Profile.objects.get(user=user)
        self.assertTrue(isinstance(profile, Profile))

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
        from django.contrib.auth import get_user_model
        from django.dispatch import Signal

        from webapp.models import Note

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
