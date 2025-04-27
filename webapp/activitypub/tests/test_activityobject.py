# Description: This file contains the test cases for the ActivityObject class.
from django.test import TestCase
from webapp.activitypub.activity import ActivityObject
from webapp.tests.rename_messages import w3c_activity


class ActivityObjectTest(TestCase):
    def setUp(self):
        self.activity = {}

    def test_activity_message_to_object(self):
        for verb, messages in w3c_activity.items():
            for message in messages:
                self.activity[verb] = ActivityObject(message)  # noqa: F841
                self.assertIsInstance(self.activity[verb], ActivityObject)

    def test_activity_object_to_message(self):
        for verb, object in self.activity.items():
                message = object.toDict()
                self.assertIsInstance(message, dict)

    def test_activity_object_repr(self):
        for verb, object in self.activity.items():
            self.assertIsInstance(object.__repr__(), str)
