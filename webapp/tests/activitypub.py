from django.test import TestCase
from django.test import Client
from webapp.tasks.activitypub import Fetch


class ActivityPubTest(TestCase):
    """
    Tests related to ActivityPub Protocol, i.e. fetching remote activities.
    """

    def setUp(self):
        """
        Setup test.
        """

        self.client = Client()

    def test_actvity_fetch(self):
        self.assertTrue(Fetch("https://pramari.de/@andreas"))

    def test_actvity_fetch_blocked(self):
        with self.assertRaises(ValueError):
            result = Fetch("https://blocked")  # noqa: F841

    def test_actvity_fetch_invalid(self):
        with self.assertRaises(ValueError):
            result = Fetch("example")  # noqa: F841

    def test_actvity_fetch_onion(self):
        with self.assertRaises(ValueError):
            activity = Fetch("http://example.onion")  # noqa: F841

    def test_activity_actor_remote(self):
        """
        test getRemoteActor helper function
        """
        from webapp.tasks.activitypub import getRemoteActor

        result = getRemoteActor("https://pramari.de/@andreas")

        self.assertEqual(result.get("id"), "https://pramari.de/@andreas")  # noqa: E501

    def test_document(self):
        from webapp.activity import ActivityMessage
        from webapp.tests.messages import w3c_activity

        from taktivitypub import APObject

        for verb, messages in w3c_activity.items():
            for message in messages:
                print(message)
                activity = ActivityMessage(message=message)  # noqa: F841
                apactivity = APObject.load(message)  # noqa: F841
                # self.assertEqual(activity.toDict(), message)
