from django.test import TestCase

class CICDTests(TestCase):
    def test_isExecuted(self):
        """
        will pass.
        """
        self.assertIs(True, True)
