"""Serializers of the reviews app."""

from rest_framework import serializers

from profile_app.api.permissions import has_profile_type
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Create and list reviews; the reviewer comes from the request."""

    class Meta:
        model = Review
        fields = [
            "id", "business_user", "reviewer", "rating", "description",
            "created_at", "updated_at",
        ]
        read_only_fields = ["reviewer", "created_at", "updated_at"]
        validators = []

    def validate_business_user(self, value):
        """Ensure the reviewed user is a business user."""
        if not has_profile_type(value, "business"):
            raise serializers.ValidationError("User is not a business user.")
        return value

    def validate(self, attrs):
        """Allow only one review per business user and reviewer."""
        reviewer = self.context["request"].user
        if Review.objects.filter(
            business_user=attrs["business_user"], reviewer=reviewer
        ).exists():
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )
        return attrs


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Update rating and description of a review."""

    class Meta:
        model = Review
        fields = [
            "id", "business_user", "reviewer", "rating", "description",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "business_user", "reviewer", "created_at", "updated_at",
        ]
