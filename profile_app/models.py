"""Data model of the profile app."""

from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Additional data of a user; either a customer or a business."""

    class ProfileType(models.TextChoices):
        """Kinds of users on the platform."""

        CUSTOMER = "customer", "Customer"
        BUSINESS = "business", "Business"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    type = models.CharField(max_length=10, choices=ProfileType.choices)
    file = models.ImageField(upload_to="profile_pictures/", blank=True)
    uploaded_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, default="")
    tel = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User profile"
        verbose_name_plural = "User profiles"
        ordering = ["user_id"]

    def __str__(self):
        """Return a readable representation for admin and shell."""
        return f"{self.user.username} ({self.type})"
