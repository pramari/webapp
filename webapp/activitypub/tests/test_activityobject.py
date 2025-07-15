# Description: This file contains the test cases for the ActivityObject class.
from django.test import TestCase
from webapp.activitypub.activity import ActivityObject
from webapp.activitypub.models import Action
from webapp.tests.rename_messages import w3c_activity
import logging
logger = logging.getLogger(__name__)

class ActivityObjectTest(TestCase):
    def setUp(self):
        self.activity = {}

    def test_activity_message_to_object(self):
        """
        Test converting activity messages to ActivityObject instances.
        """
        for verb, messages in w3c_activity.items():
            for message in messages:
                self.activity[verb] = ActivityObject(message)  # noqa: F841
                self.assertIsInstance(self.activity[verb], ActivityObject)

    def test_activity_object_to_message(self):
        """
        Test converting ActivityObject instances to activity messages.
        """
        for verb, object in self.activity.items():
                message = object.toDict()
                self.assertIsInstance(message, dict)

    def test_activity_object_repr(self):
        """
        Test converting ActivityObject instances to activity messages.
        """
        for verb, object in self.activity.items():
            self.assertIsInstance(object.__repr__(), str)

    def test_activity_object_to_action(self):
        """
        Test converting ActivityObject instances to Action instances.
        """
        for verb, messages in w3c_activity.items():
            for message in messages:
                action = ActivityObject(message).toAction()
                self.assertIsInstance(action, Action)
                self.assertEqual(action.verb, verb)
                self.assertEqual(action.object, object.toDict())
                self.assertIsInstance(action.toDict(), dict)
