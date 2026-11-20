"""Data models of the offers app."""

from django.conf import settings
from django.db import models


class Offer(models.Model):
    """A service offer of a business user with three price tiers."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offers",
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="offer_images/", null=True, blank=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ["-updated_at"]

    def __str__(self):
        """Return a readable representation for admin and shell."""
        return self.title


class OfferDetail(models.Model):
    """One price tier (basic, standard or premium) of an offer."""

    class OfferType(models.TextChoices):
        """The three tiers every offer consists of."""

        BASIC = "basic", "Basic"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name="details"
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField(help_text="-1 means unlimited.")
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=10, choices=OfferType.choices)

    class Meta:
        verbose_name = "Offer detail"
        verbose_name_plural = "Offer details"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"], name="unique_offer_type"
            ),
        ]

    def __str__(self):
        """Return a readable representation for admin and shell."""
        return f"{self.offer.title} ({self.offer_type})"
