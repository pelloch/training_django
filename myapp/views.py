from django.http import HttpResponse
from rest_framework import permissions, status, authentication
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404, ListCreateAPIView
from rest_framework.response import Response

from myapp.models import Product, Listing, Order, Merchant, OrderLine
from myapp.serializers import (
    ProductSerializer,
    ListingSerializer,
    AttachProductSerializer,
    OrderSerializer,
    OrderPushSerializer,
)


# Create your views here.
def index(request):
    return HttpResponse("Hello, my friend. You're at the MyApp index.")


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


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


class OrderAPIView(ListCreateAPIView):
    # Bonus : define a Get to see the list of orders of the authenticated merchant
    # Define a POST method to create an order with at least one orderline on existing listing
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the orders
        for the currently authenticated merchant.
        """
        merchant = get_object_or_404(Merchant.objects, user=self.request.user)
        return Order.objects.filter(merchant=merchant)

    def create(self, request, *args, **kwargs):
        # Serialize the request.data
        serializer = OrderPushSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the Order
        order = Order.objects.create(
            merchant=get_object_or_404(Merchant.objects, user=self.request.user),
            creation_date=serializer.data["creation_date"],
        )

        for ix, pk in enumerate(serializer.data["listings"]):
            # Check that every listings exist and that quantities are sufficient
            listing = get_object_or_404(Listing.objects, pk=pk)
            quantity = serializer.data["quantities"][ix]
            if quantity > listing.quantity:
                return Response(status=status.HTTP_417_EXPECTATION_FAILED)

            # Then create the associated OrderLines
            OrderLine.objects.create(order=order, listing=listing, quantity=quantity)

            # Then decrement the quantity on the listing
            new_quantity = listing.quantity - quantity
            setattr(listing, "quantity", new_quantity)
            listing.save()

        return Response(data=OrderSerializer(order).data)
