from django.http import HttpResponse
from rest_framework import permissions, renderers
from rest_framework import viewsets
from myapp.models import Product
from myapp.serializers import ProductSerializer


# Create your views here.
def index(request):
    return HttpResponse("Hello, friend. You're at the MyApp index.")


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self):
        pass


# need to define functions to create and update product (copy paste badoom)
