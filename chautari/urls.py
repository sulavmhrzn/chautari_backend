from django.contrib import admin
from django.urls import path

from chautari.views import PingView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/ping", PingView.as_view(), name="ping")
]
