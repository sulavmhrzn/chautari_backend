from django.contrib import admin
from django.urls import include, path

from chautari.views import PingView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/ping", PingView.as_view(), name="ping"),
    path("api/v1/auth/", include("apps.authentication.urls")),
]
