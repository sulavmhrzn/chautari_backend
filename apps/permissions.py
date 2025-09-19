from rest_framework.permissions import BasePermission, IsAuthenticated


class IsListingOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.seller == request.user


class IsEmailVerified(IsAuthenticated):
    message = "Verified email required"

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.email_verified
