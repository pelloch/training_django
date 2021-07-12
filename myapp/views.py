from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from models import Product, Listing


# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()