import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import encode_multipart
from django.urls import reverse
from rest_framework import status

from myapp.models import Product, Merchant


class ProductViewSetTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create the first product in DB
        cls.product = Product(pk=1, name="iPhone X de Pelloch")
        cls.product.save()

        # Create the merchant Pelloch
        cls.user = User(username="Pelloch", password="fake-password")
        cls.user.save()

        cls.merchant = Merchant.objects.create(user=cls.user)
        cls.merchant.save()

        # Data for product creation and update - need to be encoded to be handled with PUT and POST functions
        cls.data = {"name": "updated or created Product name"}
        cls.encoded_data = json.dumps(cls.data)
        cls.content_type = "application/json"

        # GET The URL to get the product pk=1
        cls.url_get = reverse("product", kwargs={"pk": cls.product.pk})

        # PUT The URL to update the product pk=1
        cls.url_put = reverse("product", kwargs={"pk": cls.product.pk})

        # POST The URL to create a product with pk=13
        cls.url_post = reverse("product", kwargs={"pk": 13})

    def test_view_should_return_404_if_no_product_created(self):
        # ARRANGE
        url_get_non_created_product = reverse("product", kwargs={"pk": 100})

        # ACT
        response = self.client.get(url_get_non_created_product)

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_return_the_correct_object(self):
        # ARRANGE
        expected_result = {"id": 1, "name": "iPhone X de Pelloch"}

        # ACT
        response = self.client.get(self.url_get)

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result)

    def test_view_cannot_update_product_if_not_authenticated(self):
        # ARRANGE

        # ACT
        request = self.client.put(
            self.url_put, data=self.encoded_data, content_type=self.content_type
        )

        # ASSERT
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_raises_404_if_update_a_non_existing_product(self):
        # ARRANGE
        self.client.force_login(user=self.merchant.user)
        url_with_a_non_existing_product = reverse("product", kwargs={"pk": 5000})

        # ACT
        request = self.client.put(
            url_with_a_non_existing_product,
            data=self.encoded_data,
            content_type=self.content_type,
        )

        # ASSERT
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_update_correctly_product(self):
        # ARRANGE
        self.client.force_login(user=self.merchant.user)
        expected_result = {"id": 1, "name": "updated or created Product name"}

        # ACT
        response = self.client.put(
            self.url_put, data=self.encoded_data, content_type=self.content_type
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result)

    def test_view_cannot_create_product_if_not_authenticated(self):
        # ARRANGE

        # ACT
        request = self.client.post(self.url_post, self.data)

        # ASSERT
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_create_correctly_product(self):
        # ARRANGE
        self.client.force_login(user=self.merchant.user)
        expected_name = "updated or created Product name"

        # ACT
        response = self.client.post(
            self.url_post, data=self.encoded_data, content_type=self.content_type
        )
        # response=post_request
        # created_product_pk = Product.objects.get(name="updated or created Product name").pk

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], expected_name)
