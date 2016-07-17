# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import CharField, BooleanField, TextField, ImageField, ForeignKey, FloatField

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import list_route, permission_classes
from rest_framework import decorators

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

class Product(models.Model):
    name = CharField(max_length=128, blank=False)
    subname = CharField(max_length=128, blank=False)
    supplier = ForeignKey('Fournisseur')
    description = TextField()
    category = ForeignKey('Categorie')
    photo = ImageField()
    price = FloatField()
    default_qtt = FloatField()
    unit = CharField(max_length=32,blank=True)
    undivisible = BooleanField(default=True)
    DISPONIBILITY_CHOICES = [
            ('invisible','invisible'),
            ('available','disponible'),
            ('unavailable','non disponible'),
            ]
    available = CharField(max_length=32,choices=DISPONIBILITY_CHOICES,default='available',blank=False)
    DELIVERY_DAYS = [
            ('monday','lundi'),
            ('tuesday','mardi'),
            ('wednesday','mercredi'),
            ('thursday','jeudi'),
            ('friday','vendredi'),
            ]
    delivery = CharField(max_length=32,choices=DELIVERY_DAYS,blank=True)

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        read_only_fields = ()

    def create(self,data):
        u = super(ProductSerializer, self).create(data)
        u.save()
        return u

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(available='available')
    serializer_class = ProductSerializer
