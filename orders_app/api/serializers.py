"""Serializers of the orders app."""

from rest_framework import serializers

from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Full, read-only representation of an order."""

    class Meta:
        model = Order
        fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """Validate the offer detail id of a new order."""

    offer_detail_id = serializers.IntegerField()


class OrderStatusSerializer(serializers.ModelSerializer):
    """Update only the status of an order."""

    class Meta:
        model = Order
        fields = ["status"]

    def validate(self, attrs):
        """Require the status and reject every other field."""
        if "status" not in attrs:
            raise serializers.ValidationError(
                {"status": "This field is required."}
            )
        unknown = set(self.initial_data) - {"status"}
        if unknown:
            raise serializers.ValidationError(
                {field: "This field cannot be updated." for field in unknown}
            )
        return attrs
