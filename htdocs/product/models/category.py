# -*- coding: utf-8 -*-
from django.db.models import Model, CharField, TextField

from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class Category(Model):
    name = CharField(max_length=128, blank=False)
    subname = CharField(max_length=128, blank=False)
    description = TextField()
    #you know what...
    
    class Meta:
        app_label = 'product'

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        read_only_fields = ()

    def create(self,data):
        u = super(CategorySerializer, self).create(data)
        u.save()
        return u

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
