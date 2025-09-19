"""
Django management command to create default categories for the student marketplace.

This command reads category data from utils.defaults.CATEGORIES and creates
Category objects in the database if they don't already exist. It uses
get_or_create to avoid duplicates based on the slug field.

Usage:
    python manage.py create_default_categories
"""

from django.core.management.base import BaseCommand

from apps.listings.models import Category
from utils.defaults import CATEGORIES


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        count = 0

        for category in CATEGORIES:
            _, created = Category.objects.get_or_create(
                slug=category.get("slug"),
                defaults={
                    "name": category.get("name"),
                    "description": category.get("description"),
                    "color": category.get("color"),
                    "slug": category.get("slug"),
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Category created: {category.get('name')}")
                )
                count += 1
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Category already exists: {category}")
                )
        self.stdout.write(self.style.SUCCESS(f"Created {count} categories"))
