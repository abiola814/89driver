from cgi import print_exception
import email
from uuid import uuid4
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from .utils import unique_otp_generator
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save

import random
import os
import requests

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, email=None, is_staff=False, is_active=True, is_admin=False):
        if not phone:
            raise ValueError('users must have a phone number')
        if not email:
            raise ValueError('user must have a password')

        user_obj = self.model(
            phone=phone,
            email=self.normalize_email(email),
        )
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj
    def create_main_user(self, phone, password=None, is_staff=False, is_active=True, is_admin=False):
        if not phone:
            raise ValueError('users must have a phone number')
        if not password:
            raise ValueError('user must have a password')

        user_obj = self.model(
            phone=phone
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj
    def create_social_user(self, email,name=None, is_staff=False, is_active=True, is_admin=False):
        if not email:
            raise ValueError('users must have a email')

        user_obj = self.model(
            email=self.normalize_email(email),
            name=name
        )
 
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj
    def create_staffuser(self, phone, password=None):
        user = self.create_main_user(
            phone,
            password=password,
            is_staff=True,


        )
        return user

    def create_superuser(self, phone, password=None):
        user = self.create_main_user(
            phone,
            password=password,
            is_staff=True,
            is_admin=True,


        )
        return user

AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email','phone':'phone'}

class User(AbstractBaseUser):
    phone_regex = RegexValidator( regex   =r'^\+?1?\d{9,14}$', message ="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.")
    phone       = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    name        = models.CharField(max_length = 20, blank = True, null = True)
    email       = models.EmailField( blank = True, null = True,unique=True)
    otp         = models.CharField(max_length = 20, blank = True, null = True)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('phone'))
    owner       = models.BooleanField(default=False)   
    standard    = models.CharField(max_length = 3, blank = True, null = True)
    score       = models.IntegerField(default = 16)
    first_login = models.BooleanField(default=False)
    active      = models.BooleanField(default=True)
    staff       = models.BooleanField(default=False)
    admin       = models.BooleanField(default=False)
    timestamp   = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    def get_full_name(self):
        return self.phone

    def get_short_name(self):
        return self.phone
    def get_email(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):

        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active
    
   



def upload_image_path_profile(instance, filename):
    new_filename = random.randint(1,9996666666)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "profile/{new_filename}/{final_filename}".format(
            new_filename=new_filename,
            final_filename=final_filename
    )
         

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


class Vehicle(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=20)
    year = models.CharField(max_length=4)
    color= models.CharField(max_length=20)


    def __str__(self):
        return str(self.id) 

class Drivers(models.Model):
    user            =   models.OneToOneField(User, on_delete= models.CASCADE)
    email           =   models.EmailField( blank = True, null = True)
    image           =   models.ImageField(upload_to = upload_image_path_profile, default=None, null = True, blank = True)
    ssn             =   models.CharField(max_length = 900, blank = True, null = True)
    driver_number   =   models.CharField(max_length = 30, blank = True, null = True)
    state            =   models.CharField(max_length = 30, blank = True, null = True)
    first_name           =   models.CharField(max_length = 30, blank = True, null = True)
    last_name           =   models.CharField(max_length = 30, blank = True, null = True)
    middle_name            =   models.CharField(max_length = 30, blank = True, null = True)
    vehicle         =   models.OneToOneField(Vehicle,on_delete=models.CASCADE,default=None,blank=True,null=True)
    first_count     =   models.IntegerField(default=0, help_text='It is 0, if the user is totally new and 1 if the user has saved his standard once' )
    driver_lat      =   models.FloatField(default=0)
    driver_long     =   models.FloatField(default=0)
    def __str__(self):
        return str(self.user) 

class Ownerprofiles(models.Model):
    user                =   models.OneToOneField(User, on_delete= models.CASCADE)
    email               =   models.EmailField( blank = True, null = True)
    image               =   models.ImageField(upload_to = upload_image_path_profile, default=None, null = True, blank = True)
    resturant_name      =   models.CharField(max_length = 900, blank = True, null = True)
    name                =   models.CharField(max_length = 900, blank = True, null = True)
    resturant_location  =   models.CharField(max_length = 199, blank = True, null = True)
    first_count         =   models.IntegerField(default=0, help_text='It is 0, if the user is totally new and 1 if the user has saved his standard once' )
    
    

    def __str__(self):
        return str(self.user) 
    
class JobRequest(models.Model):
    SMALL_SIZE='small'
    MEDIUM_SIZE='medium'
    LARGE_SIZE='large'
    SIZE=(
        (SMALL_SIZE,'small'),
        (MEDIUM_SIZE,'medium'),
        (LARGE_SIZE,'large')
    )
    Creating_status='creating'
    Active_status = 'active'
    Pending_status='pending'
    Cancel_status ='cancelled'
    Delivered_status="Delivered"
    Completed_status="completed"
    STATUSES=[
        (Creating_status,'Creating'),
        (Active_status,"active"),
        (Delivered_status,"Delivered"),
        (Cancel_status,"cancelled"),
        (Completed_status,"Completed"),
        (Pending_status,"pending")
    ]

    id                  =   models.UUIDField(primary_key=True,default=uuid4,editable=False)
    owner               =   models.ForeignKey(User,on_delete=models.CASCADE)
    description         =   models.CharField(max_length=255,blank = True, null = True)
    delivery_address    =   models.CharField(max_length=255)
    delivery_lat        =   models.CharField(max_length=15)
    delivery_long       =   models.CharField(max_length=10)
    pickup_address      =   models.CharField(max_length=255)
    pickup_lat          =   models.FloatField(default=0)
    pickup_long         =   models.FloatField(default=0)
    resturant_name      =   models.CharField(max_length = 900, blank = True, null = True)
    carier              =   models.ForeignKey(Drivers,on_delete=models.CASCADE,null=True,blank=True)
    status              =   models.CharField(max_length=255,choices=STATUSES,default=Creating_status)
    create_at           =   models.DateField(default=timezone.now)
    distance            =   models.IntegerField(default=0)
    duration            =   models.FloatField(default=0)
    price               =   models.FloatField(default=0)

    def __str__(self) -> str:
        return f"{self.resturant_name} {self.delivery_address}"

class DriverRequest(models.Model):


    Request="Request" 
    Completed="Completed"
    Accept ='Accept'
    Declined = 'Declined'
    STATUSES=(
        (Request,'Request'),
        (Accept,"Accept"),
        (Completed,"Completed"),
        (Declined,"Declined"),
        
    )

    id          =   models.UUIDField(primary_key=True,default=uuid4,editable=False)
    jobrequest  =   models.ForeignKey(JobRequest,related_name='jobrequesting',on_delete=models.CASCADE,)
    carier      =   models.ForeignKey(Drivers,on_delete=models.CASCADE,null=True,blank=True)
    status      =   models.CharField(max_length=20,choices=STATUSES,default=Request)

    def __str__(self) -> str:
        return self.status

    


class PhoneOTP(models.Model):
    phone_regex = RegexValidator( regex   =r'^\+?1?\d{9,14}$', message ="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.")
    phone       = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    otp         = models.CharField(max_length = 9, blank = True, null= True)


    def __str__(self):
        return str(self.phone) + ' is sent ' + str(self.otp)


# class Driverprofile(models.Model):
#     email= models.CharField(max_length=20)
#     phone_number=models.CharField(max_length=20)
#     otp = models.CharField(max_length=100,null=True,blank=True)
#     uid= models.UUIDField(default=uuid4)

#     def __str__(self) -> str:
#         return self.phone_number

