import logging
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from webapp.models import Profile
from webapp.signature import Signature, SignatureChecker, signedRequest
from webapp.tests.rename_messages import follow


logger = logging.getLogger(__name__)

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
        """
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
        """
        self.user = get_user_model().objects.create(username="testuser", password="testpassword")
        from webapp.tasks import genKeyPair
        self.user.profile.private_key_pem, self.user.profile.public_key_pem = genKeyPair()
        self.user.profile.save()
        """This should create private/public keys."""

    def test_request_signed(self):
        """
        Test whether a request can be signed.

        Blank Message

        .. todo::
            When calling a remote system, the remote system
            can only verify the signature if it has the public
            key. The public key is not available to the remote

            Make this issue a request to the locel system instead
        """
        import requests

        profile = Profile.objects.get(user=self.user)
        key_id = profile.actor.keyID
        message = {}

        request = signedRequest(
            "GET", "https://pramari.de/signature", message, key_id
        )  # noqa: E501

        session = requests.Session()
        response = session.send(request)  # noqa: F841

        logger.error("Signed request")
        logger.error(key_id)
        logger.error(self.user)
        logger.error(profile.actor)

        # self.assertEqual(response.text, key_id)

    def test_signature_from_header(self):
        """
        Test whether the signature is correctly parsed from the header.

        .. todo::
            RequestFactory
        """
        profile = Profile.objects.get(user=self.user)
        key_id = profile.actor.keyID

        request = signedRequest(
            "POST",
            "https://pramari.de/@andreas/inbox",
            follow,
            key_id,
        )  # noqa: E501
        signature = Signature.from_signature_header(  # noqa: E501
            request.headers["signature"]
        )  # noqa: E501
        self.assertEqual(isinstance(signature, Signature), True)

    def test_signature_validate(self):
        """
        Test whether the signature is correctly validated.

        .. todo:: This test is not working yet.
        the testhttpsignature is probably correct, but validation
        fails because the signature expired. Get a new signature
        instead. It will - or should - return None because no
        not-expired signature is parsed from **testhttpsignature.
        """
        from django.test import RequestFactory
        from webapp.signature import signedRequest

        request = RequestFactory().get(
            "/users/andreasofthings", **testhttpsignature
        )  # noqa: E501

        request = signedRequest("GET", "https://pramari.de/users/andreasofthings", {}, self.user.profile.actor.keyID)  # noqa: E501

        result = SignatureChecker().validate(request)  # noqa: E501
        self.assertEqual(result, "key_id")

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
