from rest_framework import serializers

from myapp.models import Product, Listing, Order, Orderline


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name"]


class ProductNameSerializer(serializers.Serializer):
    name = serializers.CharField()
