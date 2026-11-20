"""Permissions of the offers app."""

from rest_framework.permissions import BasePermission


class IsOfferOwner(BasePermission):
    """Allow changing an offer only for the user who created it."""

    message = "Only the creator of this offer can do this."

    def has_object_permission(self, request, view, obj):
        """Return True if the requesting user created the offer."""
        return obj.user_id == request.user.id
