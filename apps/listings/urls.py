from django.urls import path

from apps.listings.views import (
    CategoryView,
    ListingCommentView,
    ListingView,
    MyListingsView,
    SavedListingsView,
)

urlpatterns = [
    path("categories/", CategoryView.as_view(), name="categories"),
    path("", ListingView.as_view({"get": "list", "post": "create"}), name="listings"),
    path("@me/", MyListingsView.as_view({"get": "list"}), name="my-listings"),
    path(
        "@me/<slug:slug>/mark-as-sold/",
        MyListingsView.as_view({"post": "mark_as_sold"}),
        name="mark-as-sold",
    ),
    path("@me/<slug:slug>/deactivate/", MyListingsView.as_view({"post": "deactivate"})),
    path("@me/<slug:slug>/activate/", MyListingsView.as_view({"post": "activate"})),
    path(
        "@me/stats/", MyListingsView.as_view({"get": "stats"}), name="my-listings-stats"
    ),
    path(
        "@me/saved/",
        SavedListingsView.as_view({"get": "list", "post": "create"}),
        name="saved-listings",
    ),
    path(
        "<slug:slug>/",
        ListingView.as_view({"get": "retrieve", "delete": "destroy", "put": "update"}),
        name="listings-detail",
    ),
    path(
        "<slug:slug>/comments/",
        ListingCommentView.as_view({"post": "create", "get": "list"}),
    ),
]
