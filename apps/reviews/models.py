from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Review(models.Model):
    reviewed_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_reviews"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="given_reviews"
    )
    rating = models.PositiveIntegerField(
        validators=[
            MaxValueValidator(5, "rating cannot be greater than 5"),
            MinValueValidator(1, "rating cannot be less than 1"),
        ]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_reviews_user", fields=["reviewed_user", "reviewer"]
            )
        ]

    def __str__(self):
        return f"{self.reviewed_user} reviewed by {self.reviewer}"

    def clean(self):
        if self.reviewed_user == self.reviewer:
            raise ValidationError("cannot review yourself")
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
