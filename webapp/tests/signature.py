import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from webapp.models import Profile
from webapp.signature import Signature, SignatureChecker, signedRequest
from webapp.tests.messages import follow

testsignature = {
    "signature": 'keyId="https://23.social/users/andreasofthings#main-key",algorithm="rsa-sha256",headers="(request-target) host date digest content-type",signature="e5Vj4XBt9B/TJSI4iJPDW3NtAXtOM8Z6y0j72uglfSi/R1xVwUvGcgu/r0h5yaf8e5weBZcuQ7t4ztMJfQGhol2weRWqFiC5vN1SkJTnen669sX0z6JPR/9FV9piEeSLCGHdW1wscR0c1XIQNciciPB8RrgouEQxmOxPCvlXFxqQeAVRH82d5UObSU9XQOx9/j8et/lCPegQuDM00l6qmhAAwqX7UnVDrNUJgN3eYcJpOMGfGNeymdZwf3j8/CAdQGgQPfzuNmDHvy4Wo79BZV4ud9mkVquEAh7RagfwIQRUtM/mI2i2qGrXwnpjwhOgxJkjoG7Fc18qvzuT3nQfQg=="',  # noqa: E501
}  # noqa: E501

testhttpsignature = {
    "HTTP_HOST": "23.social",
    "HTTP_DATE": datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
    "HTTP_SIGNATURE": 'keyId="https://23.social/users/andreasofthings#main-key",algorithm="rsa-sha256",headers="(request-target) host date digest content-type",signature="e5Vj4XBt9B/TJSI4iJPDW3NtAXtOM8Z6y0j72uglfSi/R1xVwUvGcgu/r0h5yaf8e5weBZcuQ7t4ztMJfQGhol2weRWqFiC5vN1SkJTnen669sX0z6JPR/9FV9piEeSLCGHdW1wscR0c1XIQNciciPB8RrgouEQxmOxPCvlXFxqQeAVRH82d5UObSU9XQOx9/j8et/lCPegQuDM00l6qmhAAwqX7UnVDrNUJgN3eYcJpOMGfGNeymdZwf3j8/CAdQGgQPfzuNmDHvy4Wo79BZV4ud9mkVquEAh7RagfwIQRUtM/mI2i2qGrXwnpjwhOgxJkjoG7Fc18qvzuT3nQfQg=="',  # noqa: E501
    "HTTP_DIGEST": "SHA-256=vUwL4pc9CKe+603fymRiVnc41QkxHLpIgiHEdoGvOf8=",  # noqa: E501
    "HTTP_CONTENT_TYPE": "application/activity+json",
}  # noqa: E501


class SignatureTest(TestCase):
    def _generate_public_private_key(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )  # noqa: E501
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_key = private_key.public_key()
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return public_key_pem.decode("utf-8"), private_key_pem.decode("utf-8")

    def setUp(self):
        self.user, created = get_user_model().objects.get_or_create(
            username="testuser", password="testpassword"
        )
        from webapp.tasks import genKeyPair

        if created:
            self.user.save()

        profile = Profile.objects.get(user=self.user)
        (
            profile.private_key_pem,
            profile.public_key_pem,
        ) = genKeyPair()  # noqa: E501
        profile.save()

        """This should create private/public keys."""

    def test_request_signed(self):
        """
        Test whether a request can be signed.
        """

        user = Profile.objects.get(user=self.user)
        key_id = user.get_key_id

        ses, request = signedRequest(
            "GET", "https://pramari.de/signature", follow, key_id
        )  # noqa: E501

        response = ses.send(request)
        self.assertEqual(response.text, key_id)

    def test_signature_from_header(self):
        """
        Test whether the signature is correctly parsed from the header.
        """
        user = Profile.objects.get(user=self.user)
        key_id = user.get_key_id

        ses, request = signedRequest(
            "POST",
            "https://pramari.de/accounts/andreas/inbox",
            follow,
            key_id,
        )  # noqa: E501
        signature = Signature.from_signature_header(  # noqa: E501
            request["signature"]
        )  # noqa: E501
        self.assertEqual(isinstance(signature, Signature), True)

    def test_signature_validate(self):
        """
        Test whether the signature is correctly validated.
        """
        from django.test import RequestFactory

        request = RequestFactory().get(
            "/users/andreasofthings", **testhttpsignature
        )  # noqa: E501

        result = SignatureChecker().validate(request)  # noqa: E501
        self.assertEqual(result, True)

    def test_http_signature(self):
        from webapp.signature import HttpSignature

        public_key, private_key = self._generate_public_private_key()

        http_signature = HttpSignature().with_field("name", "value")

        signature_string = http_signature.build_signature(
            "key_id", private_key
        )  # noqa: E501

        key_id, algorithm, headers, signature = signature_string.split(",")

        assert key_id == 'keyId="key_id"'
        assert algorithm == 'algorithm="rsa-sha256"'
        assert headers == 'headers="name"'
        assert signature.startswith("signature=")
