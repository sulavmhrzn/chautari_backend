from django.conf import settings
from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Profile, User


class UserWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]

    def validate_email(self, email):
        """validates if an email is in VALID_EMAIL_DOMAINS list."""
        valid_email_domains = getattr(settings, "VALID_EMAIL_DOMAINS", [])
        _, domain = email.split("@")
        if domain not in valid_email_domains:
            raise serializers.ValidationError("not a valid college email")
        return email

    def validate_password(self, password):
        """validates password using django's `validate_password` function"""
        temp = self.Meta.model(
            email=self.initial_data.get("email"),
            first_name=self.initial_data.get("first_name"),
            last_name=self.initial_data.get("last_name"),
        )
        try:
            django_validate_password(password, temp)
        except ValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return password

    def create(self, validated_data):
        user = self.Meta.model(
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
        )
        user.set_password(validated_data.get("password"))
        user.save()
        return user


class ProfileReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["phone_number", "is_phone_number_verified"]


class ProfileWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["phone_number"]


class UserReadSerializer(serializers.ModelSerializer):
    profile = ProfileReadSerializer()

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "is_active",
            "last_login",
            "profile",
        ]
