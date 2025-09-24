import logging

from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.viewsets import ViewSet

from apps.listings.models import Listing
from apps.listings.serializers import ListingReadSerializer
from apps.profiles.serializers import UserProfileWithRecentListingsReadSerializer
from utils.constants import USER_ERRORS
from utils.envelope import Envelope

logger = logging.getLogger(__name__)
User = get_user_model()


class UserProfileViewSet(ViewSet):
    """ViewSet for handling user profile operations."""

    def get_permissions(self):
        if self.action in ["retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, user_id):
        """Get public profile of a specific user by ID."""
        try:
            user = User.objects.prefetch_related("profile", "listings").get(id=user_id)

            serializer = UserProfileWithRecentListingsReadSerializer(user)
            return Envelope.success_response(data=serializer.data)
        except User.DoesNotExist:
            return Envelope.error_response(
                error=USER_ERRORS.USER_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as exc:
            logger.error(exc)
            return Envelope.error_response(
                error="internal server error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def me(self, request):
        """Get current authenticated user's own profile."""
        serializer = UserProfileWithRecentListingsReadSerializer(request.user)
        return Envelope.success_response(data=serializer.data)


class UserListingsViewSet(ViewSet):
    """ViewSet for handling user listings operations."""

    def get_permissions(self):
        if self.action == "current_user_listings":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def retrieve(self, request, user_id):
        """Get all active listings for a specific user."""
        try:
            user = get_object_or_404(User, id=user_id)
        except Http404:
            return Envelope.error_response(
                error=USER_ERRORS.USER_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
            )
        listings = Listing.objects.filter(seller=user, is_active=True)
        serializer = ListingReadSerializer(
            listings, many=True, context={"request": request}
        )
        return Envelope.success_response(
            data={"count": len(listings), "listings": serializer.data}
        )

    def current_user_listings(self, request):
        """Get all listings (active and inactive) for the current authenticated user."""
        listings = Listing.objects.filter(seller=request.user)
        serializer = ListingReadSerializer(
            listings, many=True, context={"request": request}
        )
        return Envelope.success_response(
            data={"count": len(listings), "listings": serializer.data}
        )
