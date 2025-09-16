from django.urls import path

from apps.listings.views import CategoryView, ListingView

urlpatterns = [
    path("categories/", CategoryView.as_view(), name="categories"),
    path("", ListingView.as_view({"get": "list", "post": "create"}), name="listings"),
    path(
        "<slug:slug>/",
        ListingView.as_view({"get": "retrieve", "delete": "destroy", "put": "update"}),
        name="listings-detail",
    ),
]
