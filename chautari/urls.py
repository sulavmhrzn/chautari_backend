from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from chautari.views import PingView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/ping", PingView.as_view(), name="ping"),
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/listings/", include("apps.listings.urls")),
    path("api/v1/profiles/", include("apps.profiles.urls")),
]
if getattr(settings, "DEBUG"):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
