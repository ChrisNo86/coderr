"""Tests for registration, login and the guest user command."""

from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profile_app.models import UserProfile
from profile_app.tests.utils import create_user


class RegistrationTests(APITestCase):
    """Tests for POST /api/registration/."""

    url = reverse("registration")
    payload = {
        "username": "exampleUsername",
        "email": "example@mail.de",
        "password": "examplePassword",
        "repeated_password": "examplePassword",
        "type": "customer",
    }

    def test_registration_creates_user_and_profile(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data), {"token", "username", "email", "user_id"}
        )
        profile = UserProfile.objects.get(user_id=response.data["user_id"])
        self.assertEqual(profile.type, "customer")

    def test_password_mismatch_returns_400(self):
        data = {**self.payload, "repeated_password": "other"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_returns_400(self):
        create_user("other")
        data = {**self.payload, "email": "other@example.com"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_type_returns_400(self):
        data = {**self.payload, "type": "admin"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.exists())


class LoginTests(APITestCase):
    """Tests for POST /api/login/."""

    url = reverse("login")

    def setUp(self):
        self.user = create_user("max")

    def test_login_returns_token(self):
        data = {"username": "max", "password": "secret123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertEqual(response.data["username"], "max")

    def test_stale_token_does_not_block_login(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid")
        data = {"username": "max", "password": "secret123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_password_returns_400(self):
        data = {"username": "max", "password": "wrong"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GuestUsersCommandTests(APITestCase):
    """Tests for the create_guest_users management command."""

    def test_command_creates_both_guests_once(self):
        out = StringIO()
        call_command("create_guest_users", stdout=out)
        call_command("create_guest_users", stdout=out)
        self.assertEqual(UserProfile.objects.count(), 2)
        self.assertIn("already exists", out.getvalue())
        kevin = UserProfile.objects.get(user__username="kevin")
        self.assertEqual(kevin.type, "business")
