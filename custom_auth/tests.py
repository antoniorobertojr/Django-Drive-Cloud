from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {"username": "testuser", "password": "testpassword123"}
        self.user = User.objects.create_user(**self.user_data)

    def test_signup(self):
        url = reverse("signup")
        data = {"username": "newuser", "password": "newpassword123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

    def test_login(self):
        url = reverse("login")
        response = self.client.post(url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_token_authentication(self):
        url = reverse("test-token")
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Passed!")

    def tearDown(self):
        User.objects.all().delete()
