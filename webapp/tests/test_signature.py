from django.test import TestCase
from django.contrib.auth import get_user_model

from webapp.signature import Signature

testsignature = {
    "Signature": 'keyId="https://23.social/users/andreasofthings#main-key",algorithm="rsa-sha256",headers="(request-target) host date digest content-type",signature="e5Vj4XBt9B/TJSI4iJPDW3NtAXtOM8Z6y0j72uglfSi/R1xVwUvGcgu/r0h5yaf8e5weBZcuQ7t4ztMJfQGhol2weRWqFiC5vN1SkJTnen669sX0z6JPR/9FV9piEeSLCGHdW1wscR0c1XIQNciciPB8RrgouEQxmOxPCvlXFxqQeAVRH82d5UObSU9XQOx9/j8et/lCPegQuDM00l6qmhAAwqX7UnVDrNUJgN3eYcJpOMGfGNeymdZwf3j8/CAdQGgQPfzuNmDHvy4Wo79BZV4ud9mkVquEAh7RagfwIQRUtM/mI2i2qGrXwnpjwhOgxJkjoG7Fc18qvzuT3nQfQg=="',  # noqa: E501
}  # noqa: E501


class SignatureTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_signature_from_header(self):
        signature = Signature.from_signature_header(testsignature["Signature"])
        self.assertEqual(isinstance(signature, Signature), True)
