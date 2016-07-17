# -*- coding: utf-8 -*-
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, _user_has_module_perms, _user_has_perm
from django.db.models import CharField, EmailField, BooleanField, DateTimeField, TextField

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import list_route, permission_classes
from rest_framework import decorators

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

class MemberManager(BaseUserManager):
    def create_user(self, username, password):
        member = self.model(username=username)
        member.set_password(password)
        member.save(using=self._db)
        return member

    def create_superuser(self, username, password):
        member = self.create_user(username, password)
        member.is_superuser = True
        member.is_staff = True
        member.save(using=self._db)
        return member

class Member(AbstractBaseUser):
    class Meta:
        app_label = 'member'

    #username = CharField(max_length=128, unique=True)
    email = EmailField(max_length=254, unique=True) # one user by email, no username

    GENDER_CHOICES = (
            ('M.','Monsieur'),
            ('Mme','Madame'),
            )
    gender = CharField(max_length=3,choices=GENDER_CHOICES,default=GENDER_CHOICES[0][0])
    firstname = CharField(max_length=128, blank=False) # First and last name are mandatory
    lastname = CharField(max_length=128, blank=False)
    # phone = # didn't know how to check validity

    promotion = CharField(max_length=32, default='X2015',blank=False)

    GROUP_TYPES = [
            ('Bar','Bar'),
            ('Binet','Binet'),
            ('Événement','Événement'),
            ('Association','Association'),
            ]
    group_type = CharField(max_length=32, choices=GROUP_TYPES, blank=True) # how to put default "blank" ?
    group = CharField(max_length=128, blank=True)
    activity = TextField(max_length=256, blank=True)

    is_active = BooleanField(default=False) # maybe default False for account validation ?
    last_modified = DateTimeField(auto_now=True)
    created = DateTimeField(auto_now=True)

    is_superuser = BooleanField(default=False)
    is_admin = BooleanField(default=False)
    is_staff = BooleanField(default=False)

    previous_login = DateTimeField(blank=True, auto_now_add=True)
    current_login = DateTimeField(blank=True, auto_now_add=True)

    objects = MemberManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        PROMOTIONS = [
            ('X',2009,2015),
            ('ENSTA',2013,2016),
            ('IOGS',2013,2016),
        ]
        PROMOTIONS_CHOICES = [ ('XDoc','Doctorant') ]
        for x in PROMOTIONS:
            PROMOTIONS_CHOICES += [ (x[0]+str(i),x[0]+str(i)) for i in range(x[1],x[2]+1) ]

        self.fields['promotion'].choices = PROMOTIONS_CHOICES

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
        return self.get_full_name()

    def get_full_name(self):
        return "%s %s" % (self.firstname, self.lastname)

class MemberSerializer(ModelSerializer):
    class Meta:
        model = Member
        read_only_fields = ('is_active', 'last_login', 'last_modified', 'previous_login', 'is_staff', 'is_superuser') #champs en lecture seule
        #fields = ('id', 'username') #soit tu choisis les champs à afficher
        exclude = () # soit tu choisis les champs à cacher
        extra_kwargs = {'password': { 'write_only': True, 'required':False }} #les champs spéciaux

    def create(self, data): #on met un mot de passe par défaut (si nécessaire)
        u = super(MemberSerializer, self).create(data)
        u.set_password(data.get('password', '0000'))
        u.save()
        return u

class MemberViewSet(ModelViewSet): #ce qu'on verra dans la liste des members
    queryset = Member.objects.filter(is_active=True) #l'ensemble des éléments à sélectionner, par exemple uniquement les members dont la création de compte a été confirmée
    serializer_class = MemberSerializer #le format des éléments que tu verras
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
        member = request.user

        data = request.data
        if not member.check_password(data['old_password']):
            raise exceptions.PermissionDenied()

        if data['password'] == "":
            return Response("'password' field cannot be empty", status=HTTP_400_BAD_REQUEST)

        member.set_password(data['password'])
        member.save()
        return Response('Password changed', status=HTTP_200_OK)

    @list_route(methods=['get'])
    def list_autocomplete(self, request):
        members = Member.objects.filter(email__icontains=request.GET.get("search", "")).order_by('email')
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
    
    #là tu comprends pourquoi l'application admin n'est pas forcément utile...
    @list_route(methods=['get'])
    def list_admin(self, request):
        members = Member.objects.all().order_by('is_active', 'username')
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
