"""Admin configuration of the reviews app."""

from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin list and filters for reviews."""

    list_display = ["id", "business_user", "reviewer", "rating", "updated_at"]
    list_filter = ["rating"]
    search_fields = ["description"]
