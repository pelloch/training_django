from django.http import HttpResponse
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from myapp.models import Product
from myapp.serializers import ProductSerializer, ProductNameSerializer


# Create your views here.
def index(request):
    return HttpResponse("Hello, friend. You're at the MyApp index.")


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        # Get existing product
        product_pk = self.kwargs["pk"]
        product = get_object_or_404(Product.objects, pk=product_pk)

        # Parse input (after serializing it)
        serializer = ProductNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name_to_update = serializer.data["name"]

        # Modify product name with the serializer data
        product.name = name_to_update  # need to serialize request here to get the name
        product.save()

        return Response(data=ProductSerializer(product).data)


# need to define functions to create and update product (copy paste badoom)
