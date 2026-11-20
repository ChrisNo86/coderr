"""Shared helpers for the test suites of all apps."""

from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from offers_app.models import Offer, OfferDetail
from profile_app.models import UserProfile


def create_user(username, profile_type="customer"):
    """Create a user with a profile of the given type."""
    user = User.objects.create_user(
        username=username, email=f"{username}@example.com",
        password="secret123",
    )
    UserProfile.objects.create(user=user, type=profile_type)
    return user


def create_offer(user, title="Offer", prices=(100, 200, 300)):
    """Create an offer with basic, standard and premium details."""
    offer = Offer.objects.create(user=user, title=title, description="D")
    types = ["basic", "standard", "premium"]
    for offer_type, price, days in zip(types, prices, (3, 5, 7)):
        OfferDetail.objects.create(
            offer=offer, title=offer_type.capitalize(), revisions=1,
            delivery_time_in_days=days, price=price,
            features=["Feature"], offer_type=offer_type,
        )
    return offer


def create_image(name="test.png"):
    """Return a small in-memory PNG image upload."""
    buffer = BytesIO()
    Image.new("RGB", (2, 2)).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), "image/png")
