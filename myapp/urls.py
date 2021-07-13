from django.urls import path, include
from myapp import views
from rest_framework.routers import SimpleRouter

from myapp.views import ProductViewSet

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "product/<int:pk>",
        ProductViewSet.as_view({"get": "retrieve", "put": "update", "post": "create"}),
        name="product",
    ),
]