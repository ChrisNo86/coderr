"""Admin configuration of the orders app."""

from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin list and filters for orders."""

    list_display = [
        "id", "title", "customer_user", "business_user", "status",
        "created_at",
    ]
    list_filter = ["status", "offer_type"]
    search_fields = ["title"]
