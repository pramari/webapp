# Description: This file contains the test cases for the ActivityObject class.
from django.test import TestCase
from webapp.activity import ActivityObject
from webapp.tests.messages import w3c_activity


class ActivityObjectTest(TestCase):
    def test_activity_object(self):
        for verb, messages in w3c_activity.items():
            for message in messages:
                activity = ActivityObject(message)  # noqa: F841
