"""Serializers for registration and login."""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from profile_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration data and create a user with profile."""

    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=UserProfile.ProfileType.choices, write_only=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]
        extra_kwargs = {
            "email": {"required": True, "allow_blank": False},
            "password": {"write_only": True},
        }

    def validate_email(self, value):
        """Ensure the email address is not registered yet."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate(self, attrs):
        """Ensure both password fields match."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create the user and the matching profile in one transaction."""
        profile_type = validated_data.pop("type")
        validated_data.pop("repeated_password")
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, type=profile_type)
        return user


class LoginSerializer(serializers.Serializer):
    """Authenticate a user by username and password."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Check the credentials and attach the user."""
        user = authenticate(
            username=attrs["username"], password=attrs["password"]
        )
        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )
        attrs["user"] = user
        return attrs
