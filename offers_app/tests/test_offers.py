"""Tests for the offer and offer detail endpoints."""

import shutil
import tempfile

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from profile_app.tests.utils import create_image, create_offer, create_user

TEMP_MEDIA = tempfile.mkdtemp()


def detail_payload(offer_type, price=100):
    """Return a valid offer detail for the given type."""
    return {
        "title": offer_type, "revisions": 2, "delivery_time_in_days": 5,
        "price": price, "features": ["Logo"], "offer_type": offer_type,
    }


def details_with_basic_change(field, value):
    """Return three valid details where one field of basic is changed."""
    basic = {**detail_payload("basic"), field: value}
    return [basic, detail_payload("standard"), detail_payload("premium")]


class OfferListTests(APITestCase):
    """Tests for GET /api/offers/ incl. filters and pagination."""

    url = reverse("offer-list")

    def setUp(self):
        self.business = create_user("biz", "business")
        self.other = create_user("other", "business")
        self.cheap = create_offer(self.business, "Logo", (50, 60, 70))
        self.pricey = create_offer(self.other, "Website", (500, 600, 700))

    def test_list_is_public_and_paginated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        result = response.data["results"][0]
        self.assertEqual(result["details"][0]["url"],
                         f"/offerdetails/{result['details'][0]['id']}/")
        self.assertEqual(result["user_details"]["username"], "other")

    def test_empty_params_from_frontend_are_ignored(self):
        params = "?creator_id=&search=&ordering=&page=1&max_delivery_time="
        response = self.client.get(self.url + params)
        self.assertEqual(response.data["count"], 2)

    def test_filters(self):
        cases = {
            f"?creator_id={self.business.id}": [self.cheap.id],
            "?min_price=100": [self.pricey.id],
            "?max_delivery_time=3": [self.pricey.id, self.cheap.id],
            "?max_delivery_time=2": [],
            "?search=webs": [self.pricey.id],
            "?ordering=min_price": [self.cheap.id, self.pricey.id],
        }
        for params, expected in cases.items():
            response = self.client.get(self.url + params)
            ids = [offer["id"] for offer in response.data["results"]]
            self.assertEqual(ids, expected, params)

    def test_page_size(self):
        response = self.client.get(self.url + "?page_size=1")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIsNotNone(response.data["next"])

    def test_invalid_filter_returns_400(self):
        response = self.client.get(self.url + "?min_price=abc")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OfferCreateTests(APITestCase):
    """Tests for POST /api/offers/."""

    url = reverse("offer-list")

    def setUp(self):
        self.business = create_user("biz", "business")
        self.client.force_authenticate(self.business)

    def payload(self, details=None):
        """Return a valid offer payload."""
        types = ["basic", "standard", "premium"]
        return {
            "title": "Paket", "image": None, "description": "Desc",
            "details": details or [detail_payload(t) for t in types],
        }

    def test_business_creates_offer(self):
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["details"]), 3)
        self.assertEqual(Offer.objects.get().user, self.business)

    def test_customer_gets_403(self):
        self.client.force_authenticate(create_user("cust"))
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_gets_401(self):
        self.client.force_authenticate(None)
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_details_return_400(self):
        invalid = [
            [detail_payload("basic"), detail_payload("standard")],
            [detail_payload("basic")] * 3,
            details_with_basic_change("revisions", -2),
            details_with_basic_change("delivery_time_in_days", 0),
            details_with_basic_change("price", -1),
        ]
        for details in invalid:
            data = self.payload(details)
            response = self.client.post(self.url, data, format="json")
            self.assertEqual(response.status_code, 400, details)
        self.assertFalse(Offer.objects.exists())


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class OfferDetailTests(APITestCase):
    """Tests for GET, PATCH and DELETE /api/offers/{id}/."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.business = create_user("biz", "business")
        self.other = create_user("other", "business")
        self.offer = create_offer(self.business)
        self.url = reverse("offer-detail", args=[self.offer.id])
        self.client.force_authenticate(self.business)

    def test_retrieve_offer(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["min_price"], 100)
        self.assertEqual(response.data["min_delivery_time"], 3)
        self.assertTrue(
            response.data["details"][0]["url"].startswith("http://")
        )

    def test_retrieve_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_offer_returns_404(self):
        response = self.client.get(reverse("offer-detail", args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_updates_detail_by_type(self):
        basic = self.offer.details.get(offer_type="basic")
        data = {"title": "New", "details": [
            {"title": "Basic New", "price": 120, "offer_type": "basic"}]}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "New")
        basic.refresh_from_db()
        self.assertEqual((basic.title, basic.price), ("Basic New", 120))

    def test_patch_detail_without_type_returns_400(self):
        data = {"details": [{"title": "No type"}]}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_missing_detail_type_returns_400(self):
        self.offer.details.filter(offer_type="premium").delete()
        data = {"details": [{"price": 1, "offer_type": "premium"}]}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_image(self):
        data = {"image": create_image()}
        response = self.client.patch(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("offer_images/", response.data["image"])

    def test_foreign_business_cannot_change_offer(self):
        self.client.force_authenticate(self.other)
        patch = self.client.patch(self.url, {"title": "x"}, format="json")
        delete = self.client.delete(self.url)
        self.assertEqual(patch.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_deletes_offer(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(OfferDetail.objects.exists())

    def test_put_is_not_allowed(self):
        response = self.client.put(self.url, {}, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_str_representation(self):
        detail = self.offer.details.get(offer_type="basic")
        self.assertEqual(str(self.offer), "Offer")
        self.assertEqual(str(detail), "Offer (basic)")


class OfferDetailRetrieveTests(APITestCase):
    """Tests for GET /api/offerdetails/{id}/."""

    def setUp(self):
        self.offer = create_offer(create_user("biz", "business"))
        self.detail = self.offer.details.get(offer_type="basic")
        self.client.force_authenticate(create_user("cust"))

    def test_retrieve_detail(self):
        url = reverse("offerdetail-detail", args=[self.detail.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["offer_type"], "basic")
        self.assertEqual(response.data["features"], ["Feature"])

    def test_missing_detail_returns_404(self):
        response = self.client.get(reverse("offerdetail-detail", args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
