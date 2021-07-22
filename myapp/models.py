from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Merchant(models.Model):
    user = models.OneToOneField(User, related_name="merchant", on_delete=models.CASCADE)


class Product(models.Model):
    name = models.CharField(max_length=200, blank=False, unique=False)
    # name is mandatory


class Listing(models.Model):
    product = models.ForeignKey(
        Product,
        blank=True,
        null=True,
        default=None,
        related_name="listings",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200, blank=False)
    # title is mandatory
    description = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=False)
    # price is mandatory
    quantity = models.IntegerField(default=0)


class Order(models.Model):
    merchant = models.ForeignKey(Merchant, blank=False, on_delete=models.CASCADE)
    creation_date = models.DateTimeField("creation_date", default=timezone.now)


class OrderLine(models.Model):
    order = models.ForeignKey(
        Order, blank=False, related_name="orders", on_delete=models.CASCADE
    )
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False)
