from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import permissions, status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.viewsets import ViewSet

from apps.listings.filters import ListingFilter
from apps.listings.models import Category, Listing
from apps.listings.paginations import ListingPageNumberPagination
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
    filterset_class = ListingFilter
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["price", "created_at"]
    pagination_class = ListingPageNumberPagination

    def get_queryset(self):
        return (
            Listing.objects.filter(is_active=True)
            .select_related("seller", "category")
            .prefetch_related("images")
            .order_by("-created_at", "is_sold")
        )

    def filter_queryset(self, queryset):
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

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

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginator.paginate_queryset(queryset, self.request, self)
        serializer = ListingReadSerializer(
            page, many=True, context={"request": request}
        )
        return self.paginator.get_paginated_response(serializer.data)

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


class MyListingsView(ListingView):
    def get_permissions(self):
        return [permissions.IsAuthenticated(), IsEmailVerified()]

    def get_queryset(self):
        return Listing.objects.filter(seller=self.request.user)

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), slug=self.kwargs.get("slug"))
        self.check_object_permissions(self.request, obj)
        return obj

    def mark_as_sold(self, request, *args, **kwargs):
        """Mark listing as sold"""
        obj = self.get_object()
        obj.mark_sold()
        return Envelope.success_response(data={"detail": "marked as sold"})

    def deactivate(self, request, *args, **kwargs):
        """Deactivate listing (hide from public but keep for seller)"""
        obj = self.get_object()
        obj.mark_inactive()
        return Envelope.success_response(data={"detail": "listing deactivated"})

    def activate(self, request, *args, **kwargs):
        """Reactivate a deactivated listing"""
        obj = self.get_object()
        obj.mark_active()
        return Envelope.success_response(data={"detail": "listing activated"})

    def stats(self, request, *args, **kwargs):
        """Get seller's listing statistics"""
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total_listings=Count("id"),
            active_listings=Count("id", filter=Q(is_active=True)),
            sold_listings=Count("id", filter=Q(is_sold=True)),
            available_listings=Count("id", filter=Q(is_sold=False, is_active=True)),
        )
        return Envelope.success_response(data=stats)
