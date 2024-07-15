from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class FollowingTest(TestCase):
    def setUp(self):
        """
        Setup test.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username="user", password="password"
        )  # noqa: E501
        self.user.save()

    def test_following_html(self):
        """
        Test `/accounts/user/following`.
        Nothing more than a simple GET request.
        """
        result = self.client.get(
            reverse("profile-following", kwargs={"slug": "user"})
        )  # noqa: E501

        self.assertEqual(result.status_code, 406)
        self.assertEqual(result["Content-Type"], "text/html; charset=utf-8")

    def test_following_activity_json(self):
        """
        Test `/accounts/user/following`.
        Nothing more than a simple GET request.
        """
        result = self.client.get(
            reverse("profile-following", kwargs={"slug": "user"}),
            headers={"Accept": "application/activity+json"},
        )  # noqa: E501

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result["Content-Type"], "application/activity+json")
