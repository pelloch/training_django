from django.contrib import admin

# Register your models here.
from .models import Merchant

# admin will create only merchant, then we'll have view where merchant can create Product and Listing
admin.site.register(Merchant)