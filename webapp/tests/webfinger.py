from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model


class WebfingerTests(TestCase):
    """
    Test the webfinger endpoint
    """

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        user = User.objects.create_user(
            username="andreas", email="andreas@neumeier.org"
        )  # noqa: E501
        user.set_password("password")
        user.save()

    def test_webfinger_get_no_query(self):
        """
        Test that a GET request to /.well-known/webfinger returns a 400
        This will be the case if the resource query parameter is missing or
        empty.
        """
        response = self.client.get("/.well-known/webfinger")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["Content-Type"], "application/jrd+json")
        self.assertEqual(
            response.json(),
            {"error": "Missing resource parameter"},
        )

    def test_webfinger_get_resource(self):
        """
        Test that a GET request to /.well-known/webfinger with a resource query
        parameter returns a 200
        """
        response = self.client.get(
            "/.well-known/webfinger?resource=acct:andreas@{domain}".format(
                domain="pramari.de"
            )
        )  # noqa: E501
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/jrd+json")
        self.assertEqual(type(response.json()), type({}))
