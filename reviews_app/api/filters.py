"""Query parameter filters of the review list."""

import django_filters

from reviews_app.models import Review


class ReviewFilter(django_filters.FilterSet):
    """Filter reviews by reviewed business user and by reviewer."""

    business_user_id = django_filters.NumberFilter(
        field_name="business_user_id"
    )
    reviewer_id = django_filters.NumberFilter(field_name="reviewer_id")

    class Meta:
        model = Review
        fields = ["business_user_id", "reviewer_id"]
