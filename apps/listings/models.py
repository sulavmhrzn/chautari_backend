from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=False)
    color = models.CharField(default="#FFF")
    slug = AutoSlugField(populate_from="name", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class Listing(models.Model):
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=False)
    price = models.PositiveIntegerField()
    slug = AutoSlugField(populate_from="title", unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="listings"
    )
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    is_active = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="listing_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
