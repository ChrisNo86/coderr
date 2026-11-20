"""Permissions of the reviews app."""

from rest_framework.permissions import BasePermission


class IsReviewer(BasePermission):
    """Allow changing a review only for the user who wrote it."""

    message = "Only the creator of this review can do this."

    def has_object_permission(self, request, view, obj):
        """Return True if the requesting user wrote the review."""
        return obj.reviewer_id == request.user.id
