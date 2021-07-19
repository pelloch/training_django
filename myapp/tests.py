from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from myapp.models import Product, Merchant
from myapp.serializers import ProductSerializer


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

        # Data for product creation
        cls.data = {"name": "Product to create"}

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
        data = {"name": "new iPhone!!!"}

        # ACT
        request = self.client.put(self.url_put, data=data)

        # ASSERT
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_raises_404_if_update_a_non_existing_product(self):
        # ARRANGE
        data = {"name": "new iPhone!!!"}
        self.client.force_login(user=self.merchant.user)
        url_with_a_non_existing_product = reverse("product", kwargs={"pk": 5000})

        # ACT
        request = self.client.put(url_with_a_non_existing_product, data=data)

        # ASSERT
        self.assertEqual(request.status_code, 404)

    def test_view_update_correctly_product(self):
        # ARRANGE
        data = {"name": "new updated iPhone X for Pelloch"}
        self.client.force_login(user=self.merchant.user)
        expected_result = {"id": 1, "name": "new iPhone!!!"}

        # ACT
        update_request = self.client.put(self.url_put, data=data, format="json")

        # ASSERT
        self.assertEqual(update_request.status_code, status.HTTP_200_OK)
        self.assertEqual(update_request.data, expected_result)

    def test_view_cannot_create_product_if_not_authenticated(self):
        # ARRANGE

        # ACT
        request = self.client.post(self.url_post, self.data)

        # ASSERT
        self.assertEqual(request.status_code, 403)

    def test_view_create_correctly_product(self):
        # ARRANGE

        # ACT

        # ASSERT
        pass
