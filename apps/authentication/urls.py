from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.authentication.views import (
    CurrentUserView,
    CustomTokenObtainPairView,
    ProfileView,
    SignUpView,
)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", CurrentUserView.as_view(), name="current_user"),
    path("me/profile/", ProfileView.as_view(), name="current_user_profile"),
]
