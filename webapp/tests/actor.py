from django.conf import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class ActorTestCase(TestCase):
    """
    Test case for the actor view.
    """

    def setUp(self):
        """
        Create a user and a client for testing.

        This will trigger creation of actor properties.
        """
        User = get_user_model()
        self.client = Client()
        self.username = "andreas"
        user = User.objects.create_user(self.username)
        user.save()

    def test_actor_html(self):
        """
        Test the actor view with HTML content type.

        .. result::
            The response content type should be HTML.
            Content should be a human viewable page.
        """
        result = self.client.get(reverse("actor-view", self.username))
        self.assertEqual(result["Content-Type"], "text/html; charset=utf-8")

    def test_actor_json(self):
        result = self.client.get(
            reverse("actor-view", self.username),
            headers={"Accept": "application/json"},
            # noqa: E501
        )
        self.assertEqual(result["Content-Type"], "application/json")
