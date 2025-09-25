import logging

from django.conf import settings
from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import APIException

from utils.constants import TOKEN_ERRORS, USER_ERRORS

from .models import TOKEN_TYPES, Profile, User, VerificationToken

logger = logging.getLogger(__name__)


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
            "id",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "is_active",
            "last_login",
            "email_verified",
            "profile",
        ]


class EmailVerificationTokenSerializer(serializers.Serializer):
    token = serializers.CharField(allow_blank=False)

    def validate_token(self, value):
        """Validate token format and length."""
        if len(value) != 6:
            raise serializers.ValidationError(TOKEN_ERRORS.INVALID_FORMAT)
        return value

    def validate(self, attrs):
        """
        Validate email verification token for the authenticated user.
        Checks if token exists, belongs to user, hasn't expired, and hasn't been used.
        """
        token = attrs.get("token")
        request = self.context.get("request")
        user = request.user

        if not user:
            raise serializers.ValidationError(USER_ERRORS.USER_NOT_FOUND)

        if not token:
            raise serializers.ValidationError(TOKEN_ERRORS.TOKEN_REQUIRED)

        try:
            obj = VerificationToken.objects.get(
                token=token, token_type=TOKEN_TYPES.EMAIL_VERIFICATION, user=user
            )
        except VerificationToken.DoesNotExist:
            raise serializers.ValidationError(TOKEN_ERRORS.INVALID_TOKEN)
        except Exception as exc:
            logger.error(exc)
            raise APIException()

        if obj.is_expired():
            raise serializers.ValidationError(TOKEN_ERRORS.TOKEN_EXPIRED)

        if obj.is_used:
            raise serializers.ValidationError(TOKEN_ERRORS.TOKEN_ALREADY_USED)

        if not obj.is_valid():
            raise serializers.ValidationError(TOKEN_ERRORS.INVALID_TOKEN)

        return attrs

    def save(self, *args, **kwargs):
        """
        Mark token as used and verify user's email address.
        Returns the verification token object after successful verification.
        """
        token = self.validated_data.get("token")
        request = self.context.get("request")
        user = request.user

        obj = VerificationToken.objects.get(
            token=token, user=user, token_type=TOKEN_TYPES.EMAIL_VERIFICATION
        )
        obj.mark_as_used()
        request.user.verify_email()
        return obj


class SendResetPasswordTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_blank=False)

    def save(self, *args, **kwargs):
        """
        Create password reset token and send email.
        Always returns success for security (no email enumeration).
        """
        email = self.validated_data.get("email")
        try:
            user = User.objects.get(email=email)
            from utils.tokens import create_password_reset_token

            reset_token = create_password_reset_token(user)
            from apps.authentication.tasks import send_password_reset_email

            send_password_reset_email.delay(
                first_name=user.first_name, email=user.email, token=reset_token.token
            )
        except User.DoesNotExist:
            pass
        return {"message": "If the email exists, a reset link has been sent"}


class ResetPasswordTokenSerializer(serializers.Serializer):
    token = serializers.CharField(allow_blank=False)
    password = serializers.CharField(allow_blank=False)

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError(TOKEN_ERRORS.TOKEN_REQUIRED)
        if len(value) != 6:
            raise serializers.ValidationError(TOKEN_ERRORS.INVALID_FORMAT)
        return value

    def validate_password(self, value):
        django_validate_password(value)
        return value

    def validate(self, attrs):
        token = attrs.get("token")

        try:
            obj = VerificationToken.objects.get(
                token=token, token_type=TOKEN_TYPES.PASSWORD_RESET
            )
        except VerificationToken.DoesNotExist:
            raise serializers.ValidationError(TOKEN_ERRORS.INVALID_TOKEN)
        except Exception as exc:
            logger.error(exc)
            raise APIException()

        if obj.is_expired():
            raise serializers.ValidationError(TOKEN_ERRORS.TOKEN_EXPIRED)

        if obj.is_used:
            raise serializers.ValidationError(TOKEN_ERRORS.TOKEN_ALREADY_USED)

        if not obj.is_valid():
            raise serializers.ValidationError(TOKEN_ERRORS.INVALID_TOKEN)

        return attrs

    def save(self, **kwargs):
        """
        Mark token as used and reset user's password.
        Returns the verification token object after successful verification.
        """
        token = self.validated_data.get("token")
        raw_password = self.validated_data.get("password")

        obj = VerificationToken.objects.get(
            token=token, token_type=TOKEN_TYPES.PASSWORD_RESET
        )
        user = obj.user
        user.set_password(raw_password)
        user.save()
        obj.mark_as_used()
        return obj
