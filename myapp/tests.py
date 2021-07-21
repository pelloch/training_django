import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from myapp.models import Product, Merchant, Listing


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

        # Data for product creation and update
        # Need to be 'JSONed' to be handled with PUT and POST functions
        cls.data = {"name": "updated or created Product name"}
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
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_raises_404_if_update_a_non_existing_product(self):
        # ARRANGE
        self.client.force_login(user=self.merchant.user)
        url_with_a_non_existing_product = reverse("single-product", kwargs={"pk": 5000})

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
            self.url, data=self.encoded_data, content_type=self.content_type
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

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], expected_name)


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

        # URLs setup
        cls.url = reverse("single-listing", kwargs={"pk": cls.listing.pk})
        cls.url_create = reverse("listing")
        cls.url_attach = reverse("attach-product", kwargs={"pk": cls.listing.pk})

        # Data for listing creation and update on product_id #1
        # Need to be 'JSONed' to be handled with PUT and POST functions
        cls.data = {
            # "product": 1,
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_get_should_return_404_if_listing_not_created(self):
        # ARRANGE
        url_get_non_existing_listing = reverse("single-listing", kwargs={"pk": 100})
        self.client.force_login(user=self.merchant.user)

        # ACT
        response = self.client.get(url_get_non_existing_listing)

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
        self.client.force_login(user=self.merchant.user)

        # ACT
        response = self.client.get(self.url)

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_raises_404_if_update_a_non_existing_listing(self):
        # ARRANGE
        self.client.force_login(user=self.merchant.user)
        url_with_a_non_existing_listing = reverse("single-listing", kwargs={"pk": 5000})

        # ACT
        request = self.client.put(
            url_with_a_non_existing_listing,
            data=self.encoded_data,
            content_type=self.content_type,
        )

        # ASSERT
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_cannot_update_product(self):
        # ARRANGE

        # ACT

        # ASSERT
        pass

    def test_view_update_correctly_listing(self):
        # ARRANGE
        self.client.force_login(user=self.merchant.user)
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
            self.url, data=self.encoded_data, content_type=self.content_type
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_create_correctly_listing(self):
        # ARRANGE
        self.client.force_login(user=self.merchant.user)
        expected_result = {
            "product": None,
            "title": "iPhone X 64Gb - unlocked",
            "description": "Smartphone unlocked with all operators from Apple with 64Gb of storage capacity",
            "price": "350.00",
            "quantity": 12,
        }

        # ACT
        response = self.client.post(
            self.url_create, data=self.encoded_data, content_type=self.content_type
        )

        # ASSERT
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in expected_result.keys():
            self.assertEqual(response.data[key], expected_result[key])
