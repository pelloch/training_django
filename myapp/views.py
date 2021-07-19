from django.http import HttpResponse
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from myapp.models import Product, Listing
from myapp.serializers import ProductSerializer, ListingSerializer


# Create your views here.
def index(request):
    return HttpResponse("Hello, friend. You're at the MyApp index.")


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # Create an endpoint (via an override of the "delete" method - to be declared in the url section) that allows deleting a product and all associated listings (there is a database configuration that allows the cascade)


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
    # serializer_class = ListingSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # Listing can have null product_id. Create an endpoint PUT that allows attaching a product to a listing. Return 400 if listing already has a product

    pass
