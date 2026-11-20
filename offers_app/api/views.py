"""API views of the offers app."""

from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from offers_app.models import Offer, OfferDetail
from profile_app.api.permissions import IsBusinessUser

from .filters import OfferFilter
from .pagination import OfferPagination
from .permissions import IsOfferOwner
from .serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferWriteSerializer,
)


class OfferViewSet(viewsets.ModelViewSet):
    """List, create, retrieve, update and delete offers."""

    queryset = (
        Offer.objects.select_related("user")
        .prefetch_related("details")
        .annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )
        .order_by("-updated_at")
    )
    serializer_class = OfferWriteSerializer
    permission_classes = [IsAuthenticated]
    permission_classes_by_action = {
        "list": [AllowAny],
        "create": [IsAuthenticated & IsBusinessUser],
        "partial_update": [IsAuthenticated & IsOfferOwner],
        "destroy": [IsAuthenticated & IsOfferOwner],
    }
    pagination_class = OfferPagination
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_class = OfferFilter
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_permissions(self):
        """Return the permissions configured for the current action."""
        classes = self.permission_classes_by_action.get(
            self.action, self.permission_classes
        )
        return [permission() for permission in classes]

    def get_serializer_class(self):
        """Pick the serializer matching the current action."""
        if self.action == "list":
            return OfferListSerializer
        if self.action == "retrieve":
            return OfferRetrieveSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Set the requesting business user as creator of the offer."""
        serializer.save(user=self.request.user)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """Retrieve a single offer detail."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
