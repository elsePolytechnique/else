# -*- coding: utf-8 -*-
from django.db.models import Model, CharField, BooleanField, TextField, ImageField, ForeignKey, FloatField

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from product.models.supplier import SupplierSerializer
from product.models.category import Category

class Product(Model):
    name = CharField(max_length=128, blank=False)
    subname = CharField(max_length=128, blank=False)
    supplier = ForeignKey('Supplier')
    description = TextField()
    category = ForeignKey('Category')
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
    
    class Meta:
        app_label = 'product'

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        read_only_fields = ()
        
    #si tu veux que category soit affiché et renseigné (à la création) comme un identifiant : 
    category = PrimaryKeyRelatedField(queryset=Category.objects.all())
    
    #si tu veux que supplier soit affiché et renseigné (à la création) comme l'ensemble de ses champs : 
    supplier = SupplierSerializer()

    def create(self,data):
        u = super(ProductSerializer, self).create(data)
        u.save()
        return u

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(available='available')
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
