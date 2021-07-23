import json
from collections import OrderedDict

from django.contrib.auth.models import User
from rest_framework.test import force_authenticate
from rest_framework.authtoken.models import Token


from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from myapp.models import Product, Merchant, Listing, OrderLine, Order


class ProductViewSetTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create the first product in DB
        cls.product = Product(pk=1, name="iPhone X de Pelloch")
        cls.product.save()

        # Create the Merchant Pelloch
        cls.user = User(username="Pelloch", password="fake-password")
        cls.user.save()
        cls.merchant = Merchant.objects.create(user=cls.user)
        cls.merchant.save()
        # Fetch Token from this merchant
        cls.token = Token(user=cls.user)
        cls.token.save()

        # Data for product creation and update
        cls.data = {
            "name": "updated or created Product name",
        }
        # Need to be 'JSONed' to be handled with PUT and POST functions
        cls.encoded_data = json.dumps(cls.data)
        cls.content_type = "application/json"

        # GET or PUT - The URL to get or PUT the product pk=1
        cls.url = reverse("single-product", kwargs={"pk": cls.product.pk})

        # POST - The URL to create a product with pk=13
        cls.url_post = reverse("product")

    def test_view_get_should_return_404_if_product_not_created(self):
        # ARRANGE
        url_non_created_product = reverse("single-product", kwargs={"pk": 100})

        # ACT
        response = self.client.get(url_non_created_product)

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_get_returns_the_correct_object(self):
        # ARRANGE
        expected_result = {"id": 1, "name": "iPhone X de Pelloch"}

        # ACT
        response = self.client.get(self.url)

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result)

    def test_view_cannot_update_product_if_not_authenticated(self):
        # ARRANGE

        # ACT
        request = self.client.put(
            self.url, data=self.encoded_data, content_type=self.content_type
        )

        # ASSERT
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_raises_404_if_update_a_non_existing_product(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        url_with_a_non_existing_product = reverse("single-product", kwargs={"pk": 5000})

        # ACT
        response = self.client.put(
            url_with_a_non_existing_product,
            data=self.encoded_data,
            content_type=self.content_type,
            **header
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_update_correctly_product(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        expected_result = {"id": 1, "name": "updated or created Product name"}

        # ACT
        response = self.client.put(
            self.url, data=self.encoded_data, content_type=self.content_type, **header
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result)

    def test_view_cannot_create_product_if_not_authenticated(self):
        # ARRANGE

        # ACT
        request = self.client.post(self.url_post, self.data)

        # ASSERT
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_create_correctly_product(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        expected_name = "updated or created Product name"

        # ACT
        response = self.client.post(
            self.url_post,
            data=self.encoded_data,
            content_type=self.content_type,
            **header
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], expected_name)

    def test_view_deleting_a_product_deletes_all_associated_listings(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        # Create a product and 2 associated listings
        product_to_delete = Product(pk=2, name="product to delete")
        product_to_delete.save()
        Listing(
            pk=1, product=product_to_delete, title="listing to delete", price=12
        ).save()
        Listing(
            pk=2, product=product_to_delete, title="listing to delete", price=25
        ).save()

        url_delete = reverse("single-product", kwargs={"pk": product_to_delete.pk})
        url_listing_1 = reverse("single-listing", kwargs={"pk": 1})
        url_listing_2 = reverse("single-listing", kwargs={"pk": 2})

        # ACT
        delete_response = self.client.delete(url_delete, **header)
        get_listing_1 = self.client.get(url_listing_1, **header)
        get_listing_2 = self.client.get(url_listing_2, **header)

        # ASSERT
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(get_listing_1.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(get_listing_2.status_code, status.HTTP_404_NOT_FOUND)


class ListingViewSetTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create the first listing pk = 9 for product pk = 1
        cls.product = Product(pk=1, name="iPhone X de Pelloch")
        cls.product.save()
        cls.listing = Listing(
            pk=9,
            product=cls.product,
            title="Title name",
            description="Description text",
            price=990.00,
            quantity=120,
        )
        cls.listing.save()

        cls.listing_with_no_product = Listing(
            pk=12,
            product=None,
            title="Title name",
            description="Description text",
            price=190.90,
            quantity=3,
        )
        cls.listing_with_no_product.save()

        # Create the Merchant Pelloch
        cls.user = User(username="Pelloch", password="fake-password")
        cls.user.save()
        cls.merchant = Merchant.objects.create(user=cls.user)
        cls.merchant.save()
        # Fetch Token from this merchant
        cls.token = Token(user=cls.user)
        cls.token.save()

        # URLs setup
        cls.url = reverse("single-listing", kwargs={"pk": cls.listing.pk})
        cls.url_create = reverse("listing")
        cls.url_attach = reverse(
            "attach-product", kwargs={"pk": cls.listing_with_no_product.pk}
        )

        # Data for listing creation and update on product_id #1
        # Need to be 'JSONed' to be handled with PUT and POST functions
        cls.data = {
            "title": "iPhone X 64Gb - unlocked",
            "description": "Smartphone unlocked with all operators from Apple with 64Gb of storage capacity",
            "price": 350.00,
            "quantity": 12,
        }
        cls.encoded_data = json.dumps(cls.data)
        cls.content_type = "application/json"

    def test_view_cannot_get_listing_if_not_authenticated(self):
        # ARRANGE

        # ACT
        response = self.client.get(self.url)

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_get_should_return_404_if_listing_not_created(self):
        # ARRANGE
        url_get_non_existing_listing = reverse("single-listing", kwargs={"pk": 100})
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}

        # ACT
        response = self.client.get(url_get_non_existing_listing, **header)

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_get_returns_the_correct_object(self):
        # ARRANGE
        expected_result = {
            "id": 9,
            "product": 1,
            "title": "Title name",
            "description": "Description text",
            "price": "990.00",
            "quantity": 120,
        }
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}

        # ACT
        response = self.client.get(self.url, **header)

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result)

    def test_view_cannot_update_listing_if_not_authenticated(self):
        # ARRANGE

        # ACT
        response = self.client.put(
            self.url,
            data=self.encoded_data,
            content_type=self.content_type,
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_raises_404_if_update_a_non_existing_listing(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        url_with_a_non_existing_listing = reverse("single-listing", kwargs={"pk": 5000})

        # ACT
        request = self.client.put(
            url_with_a_non_existing_listing,
            data=self.encoded_data,
            content_type=self.content_type,
            **header
        )

        # ASSERT
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_raises_400_when_trying_update_a_product_on_a_listing_with_a_product(
        self,
    ):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        Product(pk=2, name="product 2").save()
        data = {
            "product": 2,  # updating to None shouldn't work, we expect no value at all here
            "title": "iPhone X 64Gb - unlocked",
            "price": 350.00,
        }
        encoded_data = json.dumps(data)
        content_type = "application/json"

        # ACT
        response = self.client.put(
            self.url, data=encoded_data, content_type=content_type, **header
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_update_correctly_listing(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        expected_result = {
            "id": 9,
            "product": 1,
            "title": "iPhone X 64Gb - unlocked",
            "description": "Smartphone unlocked with all operators from Apple with 64Gb of storage capacity",
            "price": "350.00",
            "quantity": 12,
        }

        # ACT
        response = self.client.put(
            self.url, data=self.encoded_data, content_type=self.content_type, **header
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result)

    def test_view_attach_product_to_listing(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        Product(pk=2, name="product 2").save()
        data = {"product": 2}
        encoded_data = json.dumps(data)
        content_type = "application/json"

        expected_result = {
            "id": 12,
            "product": 2,
            "title": "Title name",
            "description": "Description text",
            "price": "190.90",
            "quantity": 3,
        }

        # ACT
        response = self.client.put(
            self.url_attach, data=encoded_data, content_type=content_type, **header
        )

        # ASSERT
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result)

    def test_view_cannot_create_listing_if_not_authenticated(self):
        # ARRANGE

        # ACT
        response = self.client.post(
            self.url_create,
            data=self.encoded_data,
            content_type=self.content_type,
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_create_correctly_listing(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        expected_result = {
            "product": None,
            "title": "iPhone X 64Gb - unlocked",
            "description": "Smartphone unlocked with all operators from Apple with 64Gb of storage capacity",
            "price": "350.00",
            "quantity": 12,
        }

        # ACT
        response = self.client.post(
            self.url_create,
            data=self.encoded_data,
            content_type=self.content_type,
            **header
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in expected_result.keys():
            self.assertEqual(response.data[key], expected_result[key])


class OrderAPIViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create listings and associated product
        cls.product = Product(pk=1, name="iPhone X de Pelloch")
        cls.product.save()
        cls.listing_1 = Listing(
            pk=1,
            product=cls.product,
            title="Title name",
            price=990.00,
            quantity=120,
        )
        cls.listing_1.save()

        cls.listing_2 = Listing(
            pk=2,
            product=cls.product,
            title="Title name",
            price=290.00,
            quantity=2,
        )
        cls.listing_2.save()

        cls.listing_with_no_quantity = Listing(
            pk=3,
            product=cls.product,
            title="Title name",
            price=990.00,
            quantity=0,
        )
        cls.listing_with_no_quantity.save()

        # Create the Merchant Pelloch
        cls.user = User(username="Pelloch", password="fake-password")
        cls.user.save()
        cls.merchant = Merchant.objects.create(user=cls.user)
        cls.merchant.save()
        # Fetch Token from this merchant
        cls.token = Token(user=cls.user)
        cls.token.save()

        # URLs setup
        cls.url = reverse("orders")

        cls.content_type = "application/json"

    def test_view_cannot_create_order_if_not_authenticated(self):
        # ARRANGE

        # ACT
        response = self.client.post(self.url)

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_cannot_create_order_if_listing_doesnt_exist(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        data = {"listings": 13, "quantities": 1}
        encoded_data = json.dumps(data)

        # ACT
        response = self.client.post(
            self.url, data=encoded_data, content_type=self.content_type, **header
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_cannot_create_order_if_quantity_is_not_sufficient(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        data = {"listings": 2, "quantities": 3}
        encoded_data = json.dumps(data)

        # ACT
        response = self.client.post(
            self.url, data=encoded_data, content_type=self.content_type, **header
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_417_EXPECTATION_FAILED)

    def test_view_create_order_and_orderlines_properly(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        data = {
            "listings": "1,2",
            "quantities": "15,1",
            "creation_date": "2021-07-22T12:20:22.600614Z",
        }
        encoded_data = json.dumps(data)

        expected_order = {
            "id": 1,
            "merchant": self.merchant.pk,
            "creation_date": "2021-07-22T12:20:22.600614Z",
        }
        expected_orderlines = {
            1: {"id": 1, "order_id": 1, "listing_id": 1, "quantity": 15},
            2: {"id": 2, "order_id": 1, "listing_id": 2, "quantity": 1},
        }

        expected_listings_quantity = {1: 120 - 15, 2: 2 - 1}

        # ACT
        response = self.client.post(
            self.url, data=encoded_data, content_type=self.content_type, **header
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_order)

        for key, value in expected_orderlines.items():
            orderline = OrderLine.objects.filter(id=key, order_id=1)
            self.assertEqual(orderline.values()[0], value)

        for key, value in expected_listings_quantity.items():
            listing = Listing.objects.filter(id=key)
            self.assertEqual(
                listing.values()[0]["quantity"], expected_listings_quantity[key]
            )

    def test_view_cannot_get_orders_if_not_authenticated(self):
        # ARRANGE

        # ACT
        response = self.client.get(self.url)

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_get_returns_the_correct_object(self):
        # ARRANGE
        header = {"HTTP_AUTHORIZATION": "Token {}".format(self.token.key)}
        # Create a 2nd merchant
        user = User(username="Augustin", password="fake-password")
        user.save()
        merchant_2 = Merchant.objects.create(user=user)
        merchant_2.save()

        # Create orders for both merchants
        order_1 = Order(merchant=self.merchant, creation_date="2021-07-22")
        order_1.save()
        order_2 = Order(merchant=self.merchant, creation_date="2021-07-22")
        order_2.save()
        order_3 = Order(
            merchant=merchant_2, creation_date="2021-07-22T12:20:22.600614Z"
        )
        order_3.save()

        # Cannot view order from other merchant
        expected_result = [
            OrderedDict(
                {
                    "id": 1,
                    "merchant": 1,
                    "creation_date": "2021-07-22T00:00:00Z",
                }
            ),
            OrderedDict(
                {
                    "id": 2,
                    "merchant": 1,
                    "creation_date": "2021-07-22T00:00:00Z",
                },
            ),
        ]

        # ACT
        response = self.client.get(self.url, **header)

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result)
