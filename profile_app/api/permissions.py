"""Permissions of the profile app."""

from rest_framework.permissions import BasePermission


class IsProfileOwnerOrReadOnly(BasePermission):
    """Allow reading every profile but editing only the own profile."""

    message = "You can only edit your own profile."

    def has_object_permission(self, request, view, obj):
        """Return True for safe methods or if the profile is the user's."""
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return obj.user_id == request.user.id


def has_profile_type(user, profile_type):
    """Return True if the user has a profile of the given type."""
    profile = getattr(user, "profile", None)
    return profile is not None and profile.type == profile_type


class IsBusinessUser(BasePermission):
    """Allow access only for users with a business profile."""

    message = "Only business users can do this."

    def has_permission(self, request, view):
        """Return True if the requesting user is a business user."""
        return has_profile_type(request.user, "business")


class IsCustomerUser(BasePermission):
    """Allow access only for users with a customer profile."""

    message = "Only customer users can do this."

    def has_permission(self, request, view):
        """Return True if the requesting user is a customer user."""
        return has_profile_type(request.user, "customer")
