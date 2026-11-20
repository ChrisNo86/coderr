"""Tests for the profile endpoints."""

import shutil
import tempfile

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .utils import create_image, create_user

TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ProfileDetailTests(APITestCase):
    """Tests for GET and PATCH /api/profile/{pk}/."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.business = create_user("biz", "business")
        self.customer = create_user("cust")
        self.url = reverse("profile-detail", args=[self.business.id])
        self.client.force_authenticate(self.business)

    def test_get_profile_has_no_null_text_fields(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ("first_name", "last_name", "location", "tel",
                      "description", "working_hours"):
            self.assertEqual(response.data[field], "")
        self.assertEqual(response.data["type"], "business")

    def test_missing_profile_returns_404(self):
        response = self.client.get(reverse("profile-detail", args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_own_profile_with_file(self):
        data = {"first_name": "Max", "location": "Berlin",
                "email": "new@example.com", "file": create_image()}
        response = self.client.patch(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Max")
        self.assertEqual(response.data["email"], "new@example.com")
        self.business.profile.refresh_from_db()
        self.assertIsNotNone(self.business.profile.uploaded_at)

    def test_patch_foreign_profile_returns_403(self):
        self.client.force_authenticate(self.customer)
        response = self.client.patch(self.url, {"tel": "1"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_email_in_use_returns_400(self):
        data = {"email": "cust@example.com"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_str_representation(self):
        self.assertEqual(str(self.business.profile), "biz (business)")


class ProfileListTests(APITestCase):
    """Tests for the business and customer profile lists."""

    def setUp(self):
        self.business = create_user("biz", "business")
        self.customer = create_user("cust")
        self.client.force_authenticate(self.customer)

    def test_business_list(self):
        response = self.client.get(reverse("profiles-business"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([p["user"] for p in response.data],
                         [self.business.id])
        self.assertIn("working_hours", response.data[0])

    def test_customer_list(self):
        response = self.client.get(reverse("profiles-customer"))
        self.assertEqual([p["user"] for p in response.data],
                         [self.customer.id])
        self.assertIn("uploaded_at", response.data[0])

    def test_lists_require_authentication(self):
        self.client.force_authenticate(None)
        response = self.client.get(reverse("profiles-customer"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
