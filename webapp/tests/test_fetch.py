from django.test import TestCase
from django.test import Client
from webapp.tasks.activitypub import Fetch
# from webapp.tasks.activitypub import getRemoteActor


class ActivityPubTest(TestCase):
    """
    Tests related to ActivityPub Protocol, i.e. fetching remote activities.

    .. note:: This test requires internet connection to fetch remote activities.
    """

    def setUp(self):
        """
        Setup test.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.username = "andreas"
        self.client = Client()
        self.user = User.objects.create_user(
            username=self.username, password="12345", email="")
        self.actorid = self.user.profile.actor.id

    def test_actvity_fetch(self):
        """
        test Fetch function, that will get any fediverse activity.

        .. todo:: This test requires internet connection.
            It also requires a valid actor id.
            Ideally, this test should be self contained
            to work with the local test server.
        """
        # actor = Fetch(f"{self.actorid}")  # noqa: F841
        # self.assertTrue(actor)

    def test_activity_actor_remote(self):
        """
        test getRemoteActor helper function
        that will get remote actor from fediverse.

        .. todo:: This test requires internet connection.
            It also requires a valid actor id.
            Ideally, this test should be self contained
            to work with the local test server.
        """
        # result = getRemoteActor(f"{self.actorid}")  # noqa: F841
        # self.assertEqual(result.get("id"), f"{self.actorid}")  # noqa: E501

    def test_actvity_fetch_blocked(self):
        with self.assertRaises(ValueError):
            result = Fetch("https://blocked")  # noqa: F841

    def test_actvity_fetch_invalid(self):
        with self.assertRaises(ValueError):
            result = Fetch("example")  # noqa: F841

    def test_actvity_fetch_onion(self):
        with self.assertRaises(ValueError):
            activity = Fetch("http://example.onion")  # noqa: F841

