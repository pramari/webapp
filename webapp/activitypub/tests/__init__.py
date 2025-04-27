from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

accept_html = "text/html"
accept_json = "application/json"
accept_ld = "application/ld+json"
accept_jsonld_profile = (
    'application/ld+json; profile="https://www.w3.org/ns/activitystreams"'
)
accept_mastodon = "application/activity, application/ld"
accept_mastodon_json = "application/activity+json, application/ld+json"


class ActorTestCase(TestCase):
    """
    Test case for the actor view.
    """

    def setUp(self):
        """
        Create a user and a client for testing.

        This will trigger creation of actor properties.
        """
        User = get_user_model()
        self.client = Client()
        self.username = "andreas"
        user = User.objects.create_user(self.username)
        user.save()

    def test_actor_html(self):
        """
        Test the actor view with HTML content type.

        .. result::
            The response content type should be HTML.
            Content should be a human viewable page.
        """
        result = self.client.get(
            reverse("actor-view", kwargs={"slug": self.username}),
            HTTP_ACCEPT=accept_html,
        )
        self.assertEqual(result["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(result.status_code, 200)
        # self.assertRedirects(result, f"/accounts/{self.username}/")
        # actually requires login

    def test_actor_something(self):
        url = reverse("actor-view", kwargs={"slug": self.username})
        result = self.client.get(url, HTTP_ACCEPT="application/something")
        self.assertEqual(result["Content-Type"], accept_ld)
        self.assertEqual(result.status_code, 406)  # Not Acceptable

    def test_actor_mastodon(self):
        url = reverse("actor-view", kwargs={"slug": self.username})
        result = self.client.get(url, HTTP_ACCEPT=accept_mastodon)
        self.assertEqual(result["Content-Type"], accept_html)
        self.assertEqual(result.status_code, 406)  # Not Acceptable (+json is missing)

    def test_actor_mastodon_json(self):
        url = reverse("actor-view", kwargs={"slug": self.username})
        result = self.client.get(url, HTTP_ACCEPT=accept_mastodon_json)
        self.assertEqual(result["Content-Type"], "application/ld+json")
        self.assertEqual(result.status_code, 200)  # Should be acceptable

    def test_actor_ld_profile(self):
        url = reverse("actor-view", kwargs={"slug": self.username})
        result = self.client.get(url, HTTP_ACCEPT=accept_jsonld_profile)
        self.assertEqual(result["Content-Type"], accept_ld)
        self.assertEqual(result.status_code, 200)  # should be acceptable

    def test_actor_json(self):
        url = reverse("actor-view", kwargs={"slug": self.username})
        result = self.client.get(url, HTTP_ACCEPT=accept_json)
        self.assertEqual(result["Content-Type"], accept_json)
        self.assertEqual(result.status_code, 200)

    def test_serialization(self):
        """
        Test the actor serialization.
        """
        from webapp.activitypub.models import Actor

        user = get_user_model().objects.get(username=self.username)
        actor = Actor.objects.get(id=user.profile.actor.id)
        from webapp.activitypub.serializers.actor import ActorSerializer

        serialized = ActorSerializer(actor)
        self.assertEqual(serialized.data["id"], user.profile.actor.id)
