"""Serializers of the profile app."""

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from profile_app.models import UserProfile


class ProfileDetailSerializer(serializers.ModelSerializer):
    """Full profile including user data; used for GET and PATCH."""

    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", required=False, allow_blank=True,
        max_length=150,
    )
    last_name = serializers.CharField(
        source="user.last_name", required=False, allow_blank=True,
        max_length=150,
    )
    email = serializers.EmailField(source="user.email", required=False)

    class Meta:
        model = UserProfile
        fields = [
            "user", "username", "first_name", "last_name", "file",
            "location", "tel", "description", "working_hours", "type",
            "email", "created_at",
        ]
        read_only_fields = ["user", "type", "created_at"]

    def validate_email(self, value):
        """Ensure the email address is not used by another user."""
        others = User.objects.exclude(pk=self.instance.user_id)
        if others.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def update(self, instance, validated_data):
        """Update the user fields and the profile fields."""
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        if "file" in validated_data:
            validated_data["uploaded_at"] = timezone.now()
        return super().update(instance, validated_data)


class BusinessProfileListSerializer(serializers.ModelSerializer):
    """Business profile representation for the business list."""

    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = UserProfile
        fields = [
            "user", "username", "first_name", "last_name", "file",
            "location", "tel", "description", "working_hours", "type",
        ]


class CustomerProfileListSerializer(serializers.ModelSerializer):
    """Customer profile representation for the customer list."""

    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = UserProfile
        fields = [
            "user", "username", "first_name", "last_name", "file",
            "uploaded_at", "type",
        ]
