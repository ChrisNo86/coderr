"""Serializers of the offers app."""

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail

REQUIRED_OFFER_TYPES = {choice.value for choice in OfferDetail.OfferType}


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full representation of one offer detail."""

    features = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = OfferDetail
        fields = [
            "id", "title", "revisions", "delivery_time_in_days", "price",
            "features", "offer_type",
        ]

    def validate_revisions(self, value):
        """Allow a positive number of revisions or -1 for unlimited."""
        if value < -1:
            raise serializers.ValidationError(
                "Use a positive number or -1 for unlimited revisions."
            )
        return value

    def validate_delivery_time_in_days(self, value):
        """Ensure the delivery time is a positive number of days."""
        if value < 1:
            raise serializers.ValidationError("Must be at least one day.")
        return value

    def validate_price(self, value):
        """Ensure the price is not negative."""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Offer detail as id and relative URL (offer list)."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        """Return the relative path of the offer detail."""
        return f"/offerdetails/{obj.id}/"


class OfferDetailHyperlinkSerializer(serializers.ModelSerializer):
    """Offer detail as id and absolute URL (single offer)."""

    url = serializers.HyperlinkedIdentityField(view_name="offerdetail-detail")

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]


class UserDetailsSerializer(serializers.ModelSerializer):
    """Name data of the offer's creator."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class OfferListSerializer(serializers.ModelSerializer):
    """Offer representation for the paginated offer list."""

    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.FloatField(read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = UserDetailsSerializer(source="user", read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id", "user", "title", "image", "description", "created_at",
            "updated_at", "details", "min_price", "min_delivery_time",
            "user_details",
        ]


class OfferRetrieveSerializer(OfferListSerializer):
    """Offer representation for a single offer."""

    details = OfferDetailHyperlinkSerializer(many=True, read_only=True)

    class Meta(OfferListSerializer.Meta):
        fields = [
            "id", "user", "title", "image", "description", "created_at",
            "updated_at", "details", "min_price", "min_delivery_time",
        ]


class OfferWriteSerializer(serializers.ModelSerializer):
    """Create an offer with three details or update parts of it."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]

    def validate_details(self, value):
        """Check the offer types of the details for create and update."""
        types = [detail.get("offer_type") for detail in value]
        if None in types or len(types) != len(set(types)):
            raise serializers.ValidationError(
                "Every detail needs a unique offer_type."
            )
        if self.instance is None and set(types) != REQUIRED_OFFER_TYPES:
            raise serializers.ValidationError(
                "An offer needs exactly one basic, standard and premium "
                "detail."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Create the offer together with its three details."""
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)
        OfferDetail.objects.bulk_create(
            OfferDetail(offer=offer, **detail) for detail in details_data
        )
        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update the offer and the details identified by offer_type."""
        details_data = validated_data.pop("details", [])
        instance = super().update(instance, validated_data)
        for detail_data in details_data:
            self.update_detail(instance, detail_data)
        return instance

    def update_detail(self, offer, detail_data):
        """Update one existing detail of the offer, matched by type."""
        detail = offer.details.filter(
            offer_type=detail_data["offer_type"]
        ).first()
        if detail is None:
            raise serializers.ValidationError(
                {"details": "Offer has no detail of this offer_type."}
            )
        for attr, value in detail_data.items():
            setattr(detail, attr, value)
        detail.save()
