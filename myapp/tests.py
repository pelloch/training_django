from django.test import TestCase
from django.urls import reverse
from docutils.nodes import status

from myapp.models import Product
from myapp.serializers import ProductSerializer


class ProductViewSetTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = Product(pk=1, name="iPhone X de Pelloch")

        # GET The URL with a pk of the first sourcing_order (first merchant)
        cls.url_get = reverse("product", kwargs={"pk": cls.product.pk})

    def test_view_should_return_404_if_no_product_created(self):
        # ARRANGE

        # ACT
        response = self.client.get(self.url_get)

        # ASSERT
        self.assertEqual(response.status_code, 404)

    def test_view_cannot_create_product_if_not_authenticated(self):
        # ARRANGE

        # ACT
        request = self.client.post(self.url_post, self.data, format="json")

        # ASSERT
        self.assertEqual(request.status_code, 401)

        pass
