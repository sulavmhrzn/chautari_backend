from django.contrib import admin
from django.utils.html import format_html

from apps.listings.models import Category, Listing, ListingImage, SavedListing


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color")


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "seller", "is_sold", "is_active", "created_at")
    list_filter = ("seller", "is_sold", "is_active")
    search_fields = (
        "title",
        "price",
        "seller__email",
        "seller__first_name",
        "seller__last_name",
    )


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ("listing", "image_preview", "uploaded_at")

    def image_preview(self, obj):
        return format_html(
            '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
            obj.image.url,
        )

    image_preview.short_description = "Preview"


@admin.register(SavedListing)
class SavedListingAdmin(admin.ModelAdmin):
    list_display = ("user", "listing")
