from django.urls import path

from .views import UserListingsViewSet, UserProfileViewSet

urlpatterns = [
    path("me/", UserProfileViewSet.as_view({"get": "me"}), name="current_user_profile"),
    path(
        "me/listings/",
        UserListingsViewSet.as_view({"get": "current_user_listings"}),
        name="current_user_listings",
    ),
    path(
        "<int:user_id>/",
        UserProfileViewSet.as_view({"get": "retrieve"}),
        name="user_profiles",
    ),
    path(
        "<int:user_id>/listings/",
        UserListingsViewSet.as_view({"get": "retrieve"}),
        name="user_listings",
    ),
]
