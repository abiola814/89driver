

from dataclasses import fields
import email
from rest_framework import serializers
from django.contrib.auth import authenticate
from api.models import Drivers, Ownerprofiles, Vehicle,JobRequest,DriverRequest

from django.contrib.auth import get_user_model
User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', 'email')


    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):

   
    class Meta:
        model = User
        fields = ('id', 'phone', 'first_login' )

   


class LoginUserSerializer(serializers.Serializer):
    phone = serializers.CharField()


    def validate(self, attrs):
        phone = attrs.get('phone')

        if phone and email:
            if User.objects.filter(phone=phone).exists():
                user = authenticate(request=self.context.get('request'),
                                    phone=phone)
                
            else:
                msg = {'detail': 'Phone number is not registered.',
                       'register': False}
                raise serializers.ValidationError(msg)

            if not user:
                msg = {
                    'detail': 'Unable to log in with provided credentials.', 'register': True}
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class DriverSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Drivers
        fields = ('email','last_name',"middle_name","ssn","driver_number",'first_name','state','user')

class VehicleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Vehicle
        fields = ('make','color','model','year')


class OwnerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ownerprofiles
        fields = ('email','name',"resturant_name","resturant_location",'user')

class JobRequestSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = JobRequest
        fields = ('id','status','pickup_long','pickup_lat','delivery_lat','delivery_long','pickup_address','resturant_name','distance','duration','price','owner')


class RequestSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = JobRequest
        fields = ('id','carier','status')

class DriverSerializer(serializers.ModelSerializer):
    jobrequest == serializers.PrimaryKeyRelatedField(queryset=JobRequest.objects.all())
    class Meta:
        model = DriverRequest
        fields = ('jobrequest','carier','status')
