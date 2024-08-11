from django.test import TestCase
from django.contrib.auth import get_user_model

from webapp.models import Like

class WebLikeTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.username = "andreas"
        user = User.objects.create_user(username=self.username, password="password")

    def test_like_create_anonymous(self):
        self.client.get(reverse("like-create")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/like/")
        self.assertEqual(Like.objects.count(), 0)
    
    def test_like_create_authenticated(self):
        self.client.login(username=self.username, password="password")
        response = self.client.get(reverse("like-create"))
        self.assertEqual(response.status_code, 200)
        self.client.post(reverse("like-create"), data={"object": "http://example.com"})
        self.assertEqual(Like.objects.count(), 1)

    def test_like_list(self):
        response = self.client.get(reverse("like-list"))
        self.assertEqual(response.status_code, 200)

    def test_like_detail(self):
        like = Like.objects.create(object="http://example.com")
        response = self.client.get(reverse("like-detail", kwargs={"pk": like.pk}))
        self.assertEqual(response.status_code, 200)

    def test_like_delete(self):
        like = Like.objects.create(object="http://example.com")
        response = self.client.get(reverse("like-delete", kwargs={"pk": like.pk}))
        self.assertEqual(response.status_code, 200)
        self.client.post(reverse("like-delete", kwargs={"pk": like.pk}))
        self.assertEqual(Like.objects.count(), 0)