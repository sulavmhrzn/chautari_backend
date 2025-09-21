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


class LISTING_CONDITION(models.TextChoices):
    BRAND_NEW = "brand_new", "Brand New"
    BARELY_USED = "barely_used", "Barely Used"
    LIGHTLY_USED = "lightly_used", "Lightly Used"
    WELL_USED = "well_used", "Well Used"
    HEAVILY_USED = "heavily_used", "Heavily Used"
    NOT_WORKING = "not_working", "Not Working"


class Listing(models.Model):
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=False)
    price = models.PositiveIntegerField()
    slug = AutoSlugField(populate_from="title", unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="listings"
    )
    condition = models.CharField(
        max_length=100,
        choices=LISTING_CONDITION.choices,
        default=LISTING_CONDITION.BARELY_USED,
    )
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    is_active = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def mark_sold(self):
        self.is_sold = True
        self.save(update_fields=["is_sold"])


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="listing_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
