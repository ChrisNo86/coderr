"""API view with general statistics of the platform."""

from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from profile_app.models import UserProfile
from reviews_app.models import Review


class BaseInfoView(APIView):
    """Return platform statistics for the landing page (open endpoint)."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        """Return review, rating, business and offer statistics."""
        average = Review.objects.aggregate(avg=Avg("rating"))["avg"]
        return Response({
            "review_count": Review.objects.count(),
            "average_rating": round(average or 0, 1),
            "business_profile_count": UserProfile.objects.filter(
                type=UserProfile.ProfileType.BUSINESS
            ).count(),
            "offer_count": Offer.objects.count(),
        })
