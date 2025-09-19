from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.viewsets import ViewSet

from apps.listings.models import Category, Listing
from apps.listings.serializers import (
    CategoryReadSerializer,
    ListingReadSerializer,
    ListingWriteSerializer,
)
from apps.permissions import IsEmailVerified, IsListingOwner
from utils.envelope import Envelope


class CategoryView(GenericAPIView):
    def get(self, request):
        categories = Category.objects.annotate(
            listings_count=Count("listings")
        ).order_by("name")
        serializer = CategoryReadSerializer(categories, many=True)
        return Envelope.success_response(
            data={"count": len(categories), "categories": serializer.data}
        )


class ListingView(ViewSet):
    lookup_field = "slug"
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        return (
            Listing.objects.filter(is_active=True)
            .select_related("seller", "category")
            .prefetch_related("images")
            .order_by("-created_at", "is_sold")
        )

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(), slug=self.kwargs.get("slug"), is_active=True
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        elif self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated(), IsEmailVerified(), IsListingOwner()]

    def list(self, request):
        listings = self.get_queryset()
        serializer = ListingReadSerializer(
            listings, many=True, context={"request": request}
        )
        return Envelope.success_response(
            data={"count": len(listings), "listings": serializer.data}
        )

    def retrieve(self, request, slug):
        listing = get_object_or_404(self.get_queryset(), slug=slug, is_active=True)
        serializer = ListingReadSerializer(listing, context={"request": request})
        return Envelope.success_response(data=serializer.data)

    def create(self, request):
        serializer = ListingWriteSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Envelope.success_response(data=serializer.data)
        return Envelope.error_response(
            error=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, slug):
        obj = self.get_object()
        obj.delete()
        return Envelope.success_response(
            data=None, status_code=status.HTTP_204_NO_CONTENT
        )

    def update(self, request, slug):
        listing = self.get_object()
        serializer = ListingWriteSerializer(
            listing, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Envelope.success_response(data=serializer.data)

        return Envelope.error_response(
            error=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )
