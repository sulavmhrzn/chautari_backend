from django.db import transaction
from rest_framework import serializers

from .models import Category, Listing, ListingImage, User


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
            "is_sold",
            "is_active",
            "category",
            "created_at",
            "updated_at",
        )


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
        print(instance)
        images_data = validated_data.pop("images", [])
        for image_data in images_data:
            ListingImage.objects.create(listing=instance, image=image_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ListingReadSerializer(instance, context=self.context).data
