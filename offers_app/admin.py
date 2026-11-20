"""Admin configuration of the offers app."""

from django.contrib import admin

from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """Edit the three offer details directly on the offer page."""

    model = OfferDetail
    extra = 0


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin list and filters for offers."""

    list_display = ["id", "title", "user", "updated_at"]
    search_fields = ["title", "description"]
    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Admin list and filters for offer details."""

    list_display = ["id", "offer", "offer_type", "price"]
    list_filter = ["offer_type"]
