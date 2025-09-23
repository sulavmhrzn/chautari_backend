from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import Category, Listing, ListingImage, SavedListing, User


class CategoryReadSerializer(serializers.ModelSerializer):
    listings_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("name", "slug", "listings_count", "description", "color")

    def get_listings_count(self, obj):
        if hasattr(obj, "listings_count"):
            return obj.listings_count
        return obj.listings.count()


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ("id", "image")


class ListingReadSerializer(serializers.ModelSerializer):
    seller = SellerSerializer()
    category = CategorySerializer()
    images = ListingImageSerializer(many=True)
    condition = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "price",
            "seller",
            "images",
            "condition",
            "is_sold",
            "is_active",
            "category",
            "created_at",
            "updated_at",
        )

    def get_condition(self, condition):
        return condition.get_condition_display()


class ListingWriteSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), required=False)

    class Meta:
        model = Listing
        fields = (
            "title",
            "description",
            "price",
            "category",
            "images",
            "condition",
            "seller",
        )
        read_only_fields = ["seller"]

    @transaction.atomic
    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        listing = Listing.objects.create(**validated_data)
        for image_data in images_data:
            ListingImage.objects.create(listing=listing, image=image_data)
        return listing

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", [])
        for image_data in images_data:
            ListingImage.objects.create(listing=instance, image=image_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ListingReadSerializer(instance, context=self.context).data


class SavedListingReadSerializer(serializers.ModelSerializer):
    listing = ListingReadSerializer()

    class Meta:
        model = SavedListing
        fields = ["listing"]


class SavedListingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedListing
        fields = ["user", "listing"]
        read_only_fields = ["user"]

    def validate_listing(self, value):
        if not value.is_active:
            raise serializers.ValidationError("listing is deactivated")
        return value

    def save(self, **kwargs):
        user = kwargs.get("user")
        listing = self.validated_data.get("listing")
        try:
            SavedListing.objects.create(user=user, listing=listing)
            return "listing saved to your list"
        except IntegrityError:
            SavedListing.objects.get(user=user, listing=listing).delete()
            return "listing deleted from your list"
