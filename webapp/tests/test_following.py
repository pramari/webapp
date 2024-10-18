from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

accept_html = "text/html"
accept_json = "application/json"
accept_ld = "application/ld+json"
accept_jsonld_profile = (
    'application/ld+json; profile="https://www.w3.org/ns/activitystreams"'
)
accept_mastodon = "iapplication/activity, application/ld"


class FollowersTest(TestCase):
    def setUp(self):
        """
        Setup test.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username="user", password="password"
        )  # noqa: E501
        self.user.save()
        self.follower = User.objects.create(username="follower")
        self.followed = User.objects.create(username="followed")
        self.user.profile.actor.follows.add(self.follower.profile.actor)
        self.user.profile.actor.followed_by.add(self.followed.profile.actor)

    def test_followers_ld(self):
        """
        Test `/accounts/user/followers`.
        Nothing more than a simple GET request.
        """
        result = self.client.get(
            reverse("actor-followers", kwargs={"slug": "user"}),
            HTTP_ACCEPT=accept_ld,
        )  # noqa: E501
        self.assertEqual(result["Content-Type"], accept_ld)
        self.assertEqual(result.status_code, 200)


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
            reverse("actor-following", kwargs={"slug": "user"}),
            headers={"Accept": "text/html"},
        )  # noqa: E501

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result["Content-Type"], "text/html; charset=utf-8")

    def test_following_activity_json(self):
        """
        Test `/accounts/user/following`.
        Nothing more than a simple GET request.
        """
        result = self.client.get(
            reverse("actor-following", kwargs={"slug": "user"}),
            HTTP_ACCEPT=accept_ld,
        )  # noqa: E501

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result["Content-Type"], accept_ld)
