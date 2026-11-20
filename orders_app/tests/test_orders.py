"""Tests for the order endpoints."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.models import Order
from profile_app.tests.utils import create_offer, create_user


class OrderTestBase(APITestCase):
    """Fixtures: business with offer, customer, other users, one order."""

    def setUp(self):
        self.business = create_user("biz", "business")
        self.other_business = create_user("other", "business")
        self.customer = create_user("cust")
        self.other_customer = create_user("cust2")
        self.offer = create_offer(self.business)
        self.detail = self.offer.details.get(offer_type="standard")
        self.order = Order.objects.create(
            customer_user=self.customer, business_user=self.business,
            title="T", revisions=1, delivery_time_in_days=3, price=10,
            features=[], offer_type="basic",
        )
        self.order_url = reverse("order-detail", args=[self.order.id])


class OrderListCreateTests(OrderTestBase):
    """Tests for GET and POST /api/orders/."""

    url = reverse("order-list")

    def test_list_contains_only_own_orders(self):
        for user, expected in [(self.customer, 1), (self.business, 1),
                               (self.other_customer, 0)]:
            self.client.force_authenticate(user)
            response = self.client.get(self.url)
            self.assertEqual(len(response.data), expected)

    def test_customer_creates_order_from_detail(self):
        self.client.force_authenticate(self.customer)
        data = {"offer_detail_id": self.detail.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["business_user"], self.business.id)
        self.assertEqual(response.data["offer_type"], "standard")
        self.assertEqual(response.data["status"], "in_progress")

    def test_business_cannot_create_order(self):
        self.client.force_authenticate(self.business)
        data = {"offer_detail_id": self.detail.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_detail_id_returns_400(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_detail_returns_404(self):
        self.client.force_authenticate(self.customer)
        data = {"offer_detail_id": 999}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderUpdateTests(OrderTestBase):
    """Tests for PATCH /api/orders/{id}/."""

    def test_business_updates_status(self):
        self.client.force_authenticate(self.business)
        data = {"status": "completed"}
        response = self.client.patch(self.order_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(response.data["title"], "T")

    def test_invalid_status_or_field_returns_400(self):
        self.client.force_authenticate(self.business)
        for data in ({"status": "unknown"}, {"status": "completed",
                                             "price": 1}, {}):
            response = self.client.patch(self.order_url, data, format="json")
            self.assertEqual(response.status_code, 400, data)

    def test_customer_and_foreign_business_get_403(self):
        for user in (self.customer, self.other_business):
            self.client.force_authenticate(user)
            response = self.client.patch(
                self.order_url, {"status": "completed"}, format="json"
            )
            self.assertEqual(response.status_code, 403)

    def test_missing_order_returns_404(self):
        self.client.force_authenticate(self.business)
        url = reverse("order-detail", args=[999])
        response = self.client.patch(url, {"status": "completed"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_str_representation(self):
        self.assertEqual(str(self.order), f"#{self.order.id} T (in_progress)")


class OrderCountTests(OrderTestBase):
    """Tests for the order count endpoints."""

    def setUp(self):
        super().setUp()
        Order.objects.filter(pk=self.order.pk).update(status="completed")
        self.client.force_authenticate(self.customer)

    def test_counts(self):
        running = self.client.get(
            reverse("order-count", args=[self.business.id])
        )
        done = self.client.get(
            reverse("completed-order-count", args=[self.business.id])
        )
        self.assertEqual(running.data, {"order_count": 0})
        self.assertEqual(done.data, {"completed_order_count": 1})

    def test_non_business_user_returns_404(self):
        for user_id in (self.customer.id, 999):
            url = reverse("order-count", args=[user_id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
