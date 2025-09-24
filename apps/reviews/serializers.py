from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError
from rest_framework import serializers

from apps.reviews.models import Review


class ReviewWriteSerializer(serializers.ModelSerializer):
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


class ReviewReadSerializer(serializers.ModelSerializer):
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
