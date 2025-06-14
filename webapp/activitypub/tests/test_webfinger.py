from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class WebfingerTests(TestCase):
    """
    Test the webfinger endpoint
    """

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username="andreas", email="andreas@neumeier.org"
        )  # noqa: E501
        user.set_password("password")
        if created:
            user.save()

    def test_webfinger_get_no_query(self):
        """
        Test that a GET request to /.well-known/webfinger returns a 400
        This will be the case if the resource query parameter is missing or
        empty.
        """
        response = self.client.get("/.well-known/webfinger")

        self.assertEqual(
            response.status_code, 400
        )  # asuming 404 is the correct status code
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(
            response.text,
            """{"error": "Missing resource parameter"}""",
        )

    def test_webfinger_get_resource(self):
        """
        Test that a GET request to /.well-known/webfinger with a resource query
        parameter returns a 200
        """
        response = self.client.get(
            "/.well-known/webfinger?resource=acct:andreas@pramari.de"
        )
        self.assertEqual(response["Content-Type"], "application/activity+json")
        self.assertEqual(type(response.json()), type({}))
        self.assertEqual(response.status_code, 404)
