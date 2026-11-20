"""API views of the profile app."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profile_app.models import UserProfile

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    ProfileDetailSerializer,
)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve any profile; update only the own profile (PATCH)."""

    queryset = UserProfile.objects.select_related("user")
    serializer_class = ProfileDetailSerializer
    permission_classes = [IsAuthenticated & IsProfileOwnerOrReadOnly]
    http_method_names = ["get", "patch"]
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"


class BusinessProfileListView(generics.ListAPIView):
    """List all business profiles."""

    queryset = UserProfile.objects.select_related("user")
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only business profiles."""
        return self.queryset.filter(type=UserProfile.ProfileType.BUSINESS)


class CustomerProfileListView(generics.ListAPIView):
    """List all customer profiles."""

    queryset = UserProfile.objects.select_related("user")
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only customer profiles."""
        return self.queryset.filter(type=UserProfile.ProfileType.CUSTOMER)
