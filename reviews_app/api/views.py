"""API views of the reviews app."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from profile_app.api.permissions import IsCustomerUser
from reviews_app.models import Review

from .filters import ReviewFilter
from .permissions import IsReviewer
from .serializers import ReviewSerializer, ReviewUpdateSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """List reviews (filter/order) and let customers create reviews."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ["updated_at", "rating"]

    def get_permissions(self):
        """Only customers may create reviews."""
        if self.request.method == "POST":
            return [(IsAuthenticated & IsCustomerUser)()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Set the requesting customer as reviewer."""
        serializer.save(reviewer=self.request.user)


class ReviewDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    """Update (PATCH) or delete a review; only its creator may do this."""

    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsAuthenticated & IsReviewer]
    http_method_names = ["patch", "delete"]
