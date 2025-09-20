from rest_framework.permissions import BasePermission, IsAuthenticated

from utils.constants import USER_ERRORS


class IsListingOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.seller == request.user


class IsEmailVerified(IsAuthenticated):
    message = USER_ERRORS.VERIFIED_EMAIL_REQUIRED

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.email_verified
