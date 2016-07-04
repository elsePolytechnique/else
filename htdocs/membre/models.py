# -*- coding: utf-8 -*-
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, _user_has_module_perms, _user_has_perm
from django.db.models import CharField, EmailField, BooleanField, DateTimeField

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import list_route, permission_classes
from rest_framework import decorators

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

class MembreManager(BaseUserManager):
    def create_user(self, username, password):
        membre = self.model(username=username)
        membre.set_password(password)
        membre.save(using=self._db)
        return membre

    def create_superuser(self, username, password):
        membre = self.create_user(username, password)
        membre.is_superuser = True
        membre.is_staff = True
        membre.save(using=self._db)
        return membre

class Membre(AbstractBaseUser):
    class Meta:
        app_label = 'membres'

    username = CharField(max_length=128, unique=True)
    firstname = CharField(max_length=128, blank=True)
    lastname = CharField(max_length=128, blank=True)
    email = EmailField(max_length=254, blank=True)

    is_active = BooleanField(default=True)
    last_modified = DateTimeField(auto_now=True)

    is_superuser = BooleanField(default=False)
    is_staff = BooleanField(default=False)

    previous_login = DateTimeField(blank=True, auto_now_add=True)
    current_login = DateTimeField(blank=True, auto_now_add=True)

    #ajoute les champs que tu veux, genre : 
    authorised = BooleanField(default=False)

    objects = MembreManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_superuser:
            return True
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        if self.is_active and self.is_superuser:
            return True
        return _user_has_module_perms(self, app_label)

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return "%s %s" % (self.firstname, self.lastname)

class MembreSerializer(ModelSerializer):
    class Meta:
        model = Membre
        read_only_fields = ('is_active', 'last_login', 'last_modified', 'previous_login', 'is_staff', 'is_superuser') #champs en lecture seule
        #fields = ('id', 'username') #soit tu choisis les champs à afficher
        exclude = () # soit tu choisis les champs à cacher
        extra_kwargs = {'password': { 'write_only': True, 'required':False }} #les champs spéciaux

    def create(self, data): #on met un mot de passe par défaut (si nécessaire)
        u = super(MembreSerializer, self).create(data)
        u.set_password(data.get('password', '0000'))
        u.save()
        return u

class MembreViewSet(ModelViewSet): #ce qu'on verra dans la liste des membres
    queryset = Membre.objects.filter(authorised=True) #l'ensemble des éléments à sélectionner, par exemple uniquement les membres dont la création de compte a été confirmée
    serializer_class = MembreSerializer #le format des éléments que tu verras
    permission_classes = (IsAuthenticatedOrReadOnly,) #les permissions


#maintenant on définit des fonctions supplémentaires, paske juste afficher la liste de tout le monde ça sert pas à grand-chose...
    @decorators.permission_classes((IsAuthenticated,))
    @decorators.list_route(methods=['get'])
    def me(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    @decorators.permission_classes((IsAuthenticated,))
    @decorators.list_route(methods=['put'])
    def change_password(self, request):
        membre = request.user

        data = request.data
        if not membre.check_password(data['old_password']):
            raise exceptions.PermissionDenied()

        if data['password'] == "":
            return Response("'password' field cannot be empty", status=HTTP_400_BAD_REQUEST)

        membre.set_password(data['password'])
        membre.save()
        return Response('Password changed', status=HTTP_200_OK)

    @list_route(methods=['get'])
    def liste_autocomplete(self, request):
        membres = Membre.objects.filter(username__icontains=request.GET.get("recherche", "")).order_by('username')
        serializer = MembreSerializer(membres, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
    
    #là tu comprends pourquoi l'application admin n'est pas forcément utile...
    @list_route(methods=['get'])
    def liste_admin(self, request):
        membres = Membre.objects.all().order_by('authorised', 'username')
        serializer = MembreSerializer(membres, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
