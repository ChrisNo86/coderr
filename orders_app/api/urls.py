"""URL routes of the orders app."""

from django.urls import path

from .views import (
    CompletedOrderCountView,
    OrderCountView,
    OrderListCreateView,
    OrderStatusUpdateView,
)

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list"),
    path(
        "orders/<int:pk>/",
        OrderStatusUpdateView.as_view(),
        name="order-detail",
    ),
    path(
        "order-count/<int:business_user_id>/",
        OrderCountView.as_view(),
        name="order-count",
    ),
    path(
        "completed-order-count/<int:business_user_id>/",
        CompletedOrderCountView.as_view(),
        name="completed-order-count",
    ),
]
