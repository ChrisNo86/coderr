"""API views of the orders app."""

from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import OfferDetail
from orders_app.models import Order
from profile_app.api.permissions import IsBusinessUser, IsCustomerUser

from .permissions import IsOrderBusinessUser
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
)


def create_order_from_detail(detail, customer):
    """Create an order as a copy of the given offer detail."""
    return Order.objects.create(
        customer_user=customer,
        business_user=detail.offer.user,
        title=detail.title,
        revisions=detail.revisions,
        delivery_time_in_days=detail.delivery_time_in_days,
        price=detail.price,
        features=detail.features,
        offer_type=detail.offer_type,
    )


class OrderListCreateView(generics.ListCreateAPIView):
    """List the user's orders and let customers create new ones."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Only customers may create orders."""
        if self.request.method == "POST":
            return [(IsAuthenticated & IsCustomerUser)()]
        return super().get_permissions()

    def get_queryset(self):
        """Return orders where the user is customer or business."""
        user = self.request.user
        return self.queryset.filter(
            Q(customer_user=user) | Q(business_user=user)
        )

    def create(self, request, *args, **kwargs):
        """Create an order from the given offer detail id."""
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        detail = get_object_or_404(
            OfferDetail.objects.select_related("offer__user"),
            pk=serializer.validated_data["offer_detail_id"],
        )
        order = create_order_from_detail(detail, request.user)
        return Response(
            OrderSerializer(order).data, status=status.HTTP_201_CREATED
        )


class OrderStatusUpdateView(generics.UpdateAPIView):
    """Update the status of an order (business user of the order)."""

    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = [
        IsAuthenticated & IsBusinessUser & IsOrderBusinessUser
    ]
    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        """Update the status and return the full order."""
        super().update(request, *args, **kwargs)
        return Response(OrderSerializer(self.get_object()).data)


class OrderCountView(APIView):
    """Count the orders of a business user with a given status."""

    permission_classes = [IsAuthenticated]
    order_status = Order.Status.IN_PROGRESS
    response_key = "order_count"

    def get(self, request, business_user_id):
        """Return the number of matching orders or 404."""
        business_user = get_object_or_404(
            User, pk=business_user_id, profile__type="business"
        )
        count = Order.objects.filter(
            business_user=business_user, status=self.order_status
        ).count()
        return Response({self.response_key: count})


class CompletedOrderCountView(OrderCountView):
    """Count the completed orders of a business user."""

    order_status = Order.Status.COMPLETED
    response_key = "completed_order_count"
