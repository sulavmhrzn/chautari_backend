from django_filters import rest_framework as filters

from apps.listings.models import Listing


class ListingFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr="iexact")
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Listing
        fields = ["price", "condition"]
