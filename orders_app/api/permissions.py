"""Permissions of the orders app."""

from rest_framework.permissions import BasePermission


class IsOrderBusinessUser(BasePermission):
    """Allow changing an order only for its business user."""

    message = "Only the business user of this order can update it."

    def has_object_permission(self, request, view, obj):
        """Return True if the requesting user is the order's business."""
        return obj.business_user_id == request.user.id
