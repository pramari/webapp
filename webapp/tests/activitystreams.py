from django.test import TestCase


class ActivityStreamsTest(TestCase):
    def setUp(self):
        # Set up test data as before.
        pass

    def test_document(self):
        from webapp.activity import ActivityMessage
        from webapp.tests.messages import w3c_activity

        print("Testing ActivityStreams\n")
        for verb, messages in w3c_activity.items():
            print(f"Testing {verb}")
            for message in messages:
                print(f"Testing {message}")
                activity = ActivityMessage(message=message)  # noqa: F841
                # self.assertEqual(activity.toDict(), message)
