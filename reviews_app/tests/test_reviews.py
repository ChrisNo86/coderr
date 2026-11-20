"""Tests for the review endpoints."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profile_app.tests.utils import create_user
from reviews_app.models import Review


class ReviewTestBase(APITestCase):
    """Fixtures: two businesses, two customers and one review."""

    def setUp(self):
        self.business = create_user("biz", "business")
        self.other_business = create_user("other", "business")
        self.customer = create_user("cust")
        self.other_customer = create_user("cust2")
        self.review = Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=3, description="Ok",
        )
        self.detail_url = reverse("review-detail", args=[self.review.id])
        self.client.force_authenticate(self.customer)


class ReviewListCreateTests(ReviewTestBase):
    """Tests for GET and POST /api/reviews/."""

    url = reverse("review-list")

    def test_list_filter_and_ordering(self):
        Review.objects.create(business_user=self.other_business,
                              reviewer=self.customer, rating=5)
        by_business = self.client.get(
            self.url, {"business_user_id": self.business.id}
        )
        ordered = self.client.get(
            self.url, {"reviewer_id": self.customer.id, "ordering": "-rating"}
        )
        self.assertEqual([r["id"] for r in by_business.data],
                         [self.review.id])
        self.assertEqual([r["rating"] for r in ordered.data], [5, 3])

    def test_customer_creates_review(self):
        data = {"business_user": self.other_business.id, "rating": 4,
                "description": "Alles war toll!"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["reviewer"], self.customer.id)

    def test_second_review_for_same_business_returns_400(self):
        data = {"business_user": self.business.id, "rating": 4}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_data_returns_400(self):
        for data in ({"business_user": self.other_business.id, "rating": 6},
                     {"business_user": self.other_customer.id, "rating": 4}):
            response = self.client.post(self.url, data, format="json")
            self.assertEqual(response.status_code, 400, data)

    def test_business_cannot_create_review(self):
        self.client.force_authenticate(self.other_business)
        data = {"business_user": self.business.id, "rating": 4}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewUpdateDeleteTests(ReviewTestBase):
    """Tests for PATCH and DELETE /api/reviews/{id}/."""

    def test_reviewer_updates_rating_and_description_only(self):
        data = {"rating": 5, "description": "Noch besser",
                "business_user": self.other_business.id}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["business_user"], self.business.id)

    def test_invalid_rating_returns_400(self):
        response = self.client.patch(self.detail_url, {"rating": 0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_user_gets_403(self):
        self.client.force_authenticate(self.other_customer)
        patch = self.client.patch(self.detail_url, {"rating": 1})
        delete = self.client.delete(self.detail_url)
        self.assertEqual(patch.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviewer_deletes_review(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.exists())

    def test_missing_review_returns_404(self):
        url = reverse("review-detail", args=[999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_str_representation(self):
        self.assertEqual(str(self.review), "cust -> biz: 3")
