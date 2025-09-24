from django.urls import path

from apps.reviews.views import ReviewViewSet, UserReviewViewSet

urlpatterns = [
    path("", ReviewViewSet.as_view({"get": "list", "post": "create"}), name="reviews"),
    path(
        "user/<int:user_id>/",
        UserReviewViewSet.as_view({"get": "list"}),
        name="user_reviews",
    ),
]
