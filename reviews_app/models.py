"""Data model of the reviews app."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """A rating a customer gives a business user (one per business)."""

    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_reviews",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="written_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["business_user", "reviewer"],
                name="one_review_per_business",
            ),
        ]

    def __str__(self):
        """Return a readable representation for admin and shell."""
        return f"{self.reviewer} -> {self.business_user}: {self.rating}"
