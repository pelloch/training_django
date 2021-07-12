from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Merchant(models.Model):
    user = models.OneToOneField(User, related_name="merchant", on_delete=models.CASCADE)


class Product(models.Model):
    name = models.CharField(max_length=200, blank=True)


class Listing(models.Model):
    product = models.ForeignKey(Product, blank=True, null=True, default=None, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=200, blank=True)


class Order(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    creation_date = models.DateTimeField("date creation", default=timezone.now)


class Orderline(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)


