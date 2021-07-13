from django.http import HttpResponse
from rest_framework import permissions, renderers
from rest_framework import viewsets
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
        product_pk = self.kwargs["pk"]
        product = Product.objects.get(pk=product_pk)
        product.name = request.data[
            "name"
        ]  # need to serialize request here to get the name
        product.save()
        return Response(data=ProductSerializer(product).data)


# need to define functions to create and update product (copy paste badoom)
