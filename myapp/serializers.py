from ddtrace.compat import is_integer
from rest_framework import serializers
from django.utils import timezone


from myapp.models import Product, Listing, Order, OrderLine


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


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "merchant", "creation_date"]


class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ["id", "order", "listing", "quantity"]


class OrderPushSerializer(serializers.Serializer):
    listings = serializers.ListField(child=serializers.IntegerField())
    quantities = serializers.ListField(child=serializers.IntegerField())
    creation_date = serializers.DateTimeField(default=timezone.now())

    def to_internal_value(self, data):
        # Convert single integer to list of 1 element
        if is_integer(data["listings"]):
            data["listings"] = [data["listings"]]
            data["quantities"] = [data["quantities"]]
            return data

        # Convert comma separated digits to list of integers
        data["listings"] = data["listings"].split(",") if data["listings"] else []
        data["quantities"] = data["quantities"].split(",") if data["quantities"] else []
        return data
