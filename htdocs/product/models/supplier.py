# -*- coding: utf-8 -*-
from django.db.models import Model, CharField, TextField, ImageField

from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class Supplier(Model):
    name = CharField(max_length=128, blank=False)
    subname = CharField(max_length=128, blank=False)
    description = TextField()
    photo = ImageField()
    
    class Meta:
        app_label = 'product'

class SupplierSerializer(ModelSerializer):
    class Meta:
        model = Supplier
        read_only_fields = ()

    def create(self,data):
        u = super(SupplierSerializer, self).create(data)
        u.save()
        return u

class SupplierViewSet(ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
