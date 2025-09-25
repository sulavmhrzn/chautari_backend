from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError
from rest_framework import serializers

from apps.reviews.models import Review


class ReviewWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for writing reviews.

    This serializer handles validation and creation of Review objects, ensuring that:
    - The reviewer cannot review themselves.
    - Duplicate reviews are prevented (raises a validation error if a review already exists).
    - Django validation errors are properly surfaced as serializer validation errors.

    Fields:
        reviewed_user (int): The ID of the user being reviewed.
        reviewer (int, read-only): The ID of the user writing the review.
        rating (int): The rating given in the review.
        comment (str): The textual comment of the review.
    """

    class Meta:
        model = Review
        fields = ["reviewed_user", "reviewer", "rating", "comment"]
        read_only_fields = ["reviewer"]

    def validate_reviewed_user(self, value):
        request = self.context.get("request")
        user = request.user
        reviewed_user = self.initial_data.get("reviewed_user")
        if reviewed_user == user.id:
            raise serializers.ValidationError("cannot review yourself")
        return value

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except IntegrityError:
            raise serializers.ValidationError("review already exists")
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message)


class ReviewUpdateSerializer(ReviewWriteSerializer):
    """
    Serializer for updating Review instances.

    Inherits from ReviewWriteSerializer and restricts modification of the 'reviewed_user' and 'reviewer' fields,
    making them read-only during update operations. This ensures that the users associated with a review cannot be changed
    when updating the review details.

    For use in PATCH or PUT requests where only editable fields should be updated.
    """

    class Meta(ReviewWriteSerializer.Meta):
        read_only_fields = ["reviewed_user", "reviewer"]


class ReviewReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading Review objects.

    Fields:
        - id: Integer, unique identifier for the review.
        - reviewed_user: String representation of the user being reviewed.
        - reviewer: String representation of the user who wrote the review.
        - rating: Integer, rating given in the review.
        - comment: String, textual comment of the review.
        - can_delete: Boolean, indicates if the current user can delete this review (True if the user is the reviewer).
        - can_edit: Boolean, indicates if the current user can edit this review (True if the user is the reviewer).

    Methods:
        - get_can_delete(instance): Returns True if the current user is the reviewer, otherwise False.
        - get_can_edit(instance): Returns True if the current user is the reviewer, otherwise False.

    Context:
        Expects 'request' in serializer context to determine permissions for 'can_delete' and 'can_edit'.
    """

    reviewed_user = serializers.StringRelatedField()
    reviewer = serializers.StringRelatedField()
    can_delete = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "reviewed_user",
            "reviewer",
            "rating",
            "comment",
            "can_delete",
            "can_edit",
        ]

    def get_can_delete(self, instance):
        request = self.context.get("request", {})
        if not hasattr(request, "user"):
            return False
        return request.user == instance.reviewer

    def get_can_edit(self, instance):
        request = self.context.get("request", {})
        if not hasattr(request, "user"):
            return False
        return request.user == instance.reviewer
