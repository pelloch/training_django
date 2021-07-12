from rest_framework import serializers
from models import Product, Listing, Order, Orderline


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields= ["id","name"]