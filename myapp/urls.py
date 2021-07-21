from django.urls import path
from myapp import views

from myapp.views import ProductViewSet, ListingViewSet

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "product/",
        ProductViewSet.as_view({"get": "list", "post": "create"}),
        name="product",
    ),
    path(
        "product/<int:pk>",
        ProductViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="single-product",
    ),
    path(
        "get_listing/<int:pk>",
        ListingViewSet.as_view({"put": "update"}),
        name="attach-listing",
    ),
    path(
        "listing/",
        ListingViewSet.as_view({"get": "list", "post": "create"}),
        name="listing",
    ),
    path(
        "listing/<int:pk>",
        ListingViewSet.as_view({"get": "retrieve", "put": "update"}),
        name="single-listing",
    ),
    path(
        "listing/<int:pk>/attach-product",
        ListingViewSet.as_view({"put": "attach_product"}),
        name="attach-product",
    ),
]
