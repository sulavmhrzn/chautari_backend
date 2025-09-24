from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.listings.serializers import ListingReadSerializer

User = get_user_model()


class UserProfileWithRecentListingsReadSerializer(serializers.ModelSerializer):
    recent_listings = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "date_joined", "recent_listings"]

    def to_representation(self, instance):
        """Add phone number to the serialized user data."""
        repr = super().to_representation(instance)
        repr["phone_number"] = (
            instance.profile.phone_number.as_international
            if instance.profile.phone_number
            else None
        )

        return repr

    def get_recent_listings(self, instance):
        """Retrieve and serialize the 6 most recent listings."""
        recent_listings = ListingReadSerializer(
            instance.listings.order_by("-created_at")[:6], many=True
        )
        return recent_listings.data
