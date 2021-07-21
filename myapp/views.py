from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from myapp.models import Product, Listing
from myapp.serializers import (
    ProductSerializer,
    ListingSerializer,
    AttachProductSerializer,
)


# Create your views here.
def index(request):
    return HttpResponse("Hello, friend. You're at the MyApp index.")


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # Create an endpoint (via an override of the "delete" method - to be declared in the url section)
    # that allows deleting a product and all associated listings
    # (there is a database configuration that allows the cascade)
    # Maybe, we just need to test the delete function and ensure that cascade is working


"""
# Finally, no need to create this update method as it's handled automatically by ModelViewSet
    def update(self, request, *args, **kwargs):
        # Get existing product
        product_pk = self.kwargs["pk"]
        product = get_object_or_404(Product.objects, pk=product_pk)

        # Parse input (after serializing it)
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name_to_update = serializer.data["name"]

        # Modify product name with the serializer data
        product.name = name_to_update
        product.save()

        return Response(data=ProductSerializer(product).data)
"""


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        # Get existing product
        listing_pk = self.kwargs["pk"]
        listing = get_object_or_404(Listing.objects, pk=listing_pk)

        # Serialize input and check that request.data is valid
        serializer = ListingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        # Return 400 if update want to update product
        # This feature is only handled by attach_product
        if data.get("product") is not None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Update all fields of the listing except the product
        data["product"] = listing.product
        for key in data:
            setattr(listing, key, data[key])
        listing.save()

        return Response(data=ListingSerializer(listing).data)

    def attach_product(self, request, *args, **kwarg):
        """Endpoint PUT that allows attaching a product to a listing.
        Returns 400 if listing already has a product"""
        listing_pk = self.kwargs["pk"]
        listing = get_object_or_404(Listing.objects, pk=listing_pk)

        # Serialize input and check that request.data is valid
        serializer = AttachProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Replace product of the listing by the product from the request
        product = get_object_or_404(Product.objects, pk=serializer.data["product"])
        setattr(listing, "product", product)

        return Response(data=ListingSerializer(listing).data)
