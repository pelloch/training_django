from rest_framework import serializers

from myapp.models import Product, Listing


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name"]


class ListingSerializer(serializers.ModelSerializer):

    """
    # this doesn't work if applied - don't understand why (copy / paste from badoom)
    id = serializers.CharField()
    product_id = serializers.IntegerField(source="product")
    title = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    quantity = serializers.IntegerField()
    """

    class Meta:
        model = Listing
        fields = ["id", "product", "title", "description", "price", "quantity"]


class AttachProductSerializer(serializers.Serializer):
    product = serializers.IntegerField()
