"""Tests for GET /api/base-info/."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profile_app.tests.utils import create_offer, create_user
from reviews_app.models import Review


class BaseInfoTests(APITestCase):
    """Tests for the platform statistics."""

    url = reverse("base-info")

    def test_empty_platform(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "review_count": 0, "average_rating": 0,
            "business_profile_count": 0, "offer_count": 0,
        })

    def test_statistics_are_public_and_rounded(self):
        business = create_user("biz", "business")
        create_offer(business)
        for name, rating in (("a", 4), ("b", 5), ("c", 5)):
            Review.objects.create(business_user=business,
                                  reviewer=create_user(name), rating=rating)
        response = self.client.get(self.url)
        self.assertEqual(response.data["review_count"], 3)
        self.assertEqual(response.data["average_rating"], 4.7)
        self.assertEqual(response.data["business_profile_count"], 1)
        self.assertEqual(response.data["offer_count"], 1)
