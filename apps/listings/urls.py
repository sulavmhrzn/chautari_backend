from django.urls import path

from apps.listings.views import CategoryView, ListingView, MyListingsView

urlpatterns = [
    path("categories/", CategoryView.as_view(), name="categories"),
    path("", ListingView.as_view({"get": "list", "post": "create"}), name="listings"),
    path("@me/", MyListingsView.as_view({"get": "list"}), name="my-listings"),
    path(
        "@me/<slug:slug>/mark-as-sold/",
        MyListingsView.as_view({"patch": "mark_as_sold"}),
        name="mark-as-sold",
    ),
    path(
        "<slug:slug>/",
        ListingView.as_view({"get": "retrieve", "delete": "destroy", "put": "update"}),
        name="listings-detail",
    ),
]
