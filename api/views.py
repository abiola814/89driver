
import requests
from django.contrib.auth import login
from django.db.models import Q
from django.shortcuts import get_object_or_404
from knox.auth import TokenAuthentication
from knox.views import LoginView as KnoxLoginView
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .message import MessageHandler
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from .models import Ownerprofiles, PhoneOTP, User,Drivers, Vehicle,JobRequest,DriverRequest,Rating,Notice
from .serializer import CreateUserSerializer, CreateAdminUserSerializer,DriverSerializers,OwnerSerializer, LoginUserSerializer,DriverSerializer,VehicleSerializer,JobRequestSerializer,RequestSerializer,DriverSerializers
from .utils import otp_generator, password_generator, phone_validator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


        

class ValidatePhoneSendOTP(GenericAPIView):


    
    test_param =openapi.Parameter("email",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    phone_param =openapi.Parameter("phone",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary='validating of register',manual_parameters=[test_param,phone_param],operation_description='  This class view takes phone number and email and if it does not exists already then it sends otp forfirst coming phone numbers'
    ,responses={200:'successfull','status':"true",'detail':'infomation of what happened'})
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact = phone)
            if user.exists():
                return Response({'status': False, 'detail': 'Phone Number already exists'})
                 # logic to send the otp and store the phone number and that otp in table. 
            else:
                otp = 1234#otp_generator()
                try:
                    #send_otp=MessageHandler(phone,otp).send_otp()
                    send_otp=1234
                except:
                    return Response({'status': False, 'detail': ' unable to send otp check the number again '})


                print(send_otp)
                print(phone, otp)
                if send_otp:
                    otp = str(otp)
                    old = PhoneOTP.objects.filter(phone__iexact = phone)
                    if old.exists():
                        new_otp = PhoneOTP.objects.get(phone__iexact = phone)
                        new_otp.otp=otp
                        new_otp.save()
                    else:
               
                        PhoneOTP.objects.create(
                             phone =  phone, 
                             otp =   otp,
        
                             )
                    
                else:
                    return Response({
                                'status': 'False', 'detail' : "OTP sending error. Please try after some time."
                            })

                return Response({
                    'status': True, 'detail': 'Otp has been sent successfully.'
                })
        else:
            return Response({
                'status': 'False', 'detail' : "I haven't received any phone number. Please do a POST request."
            })

class Register(GenericAPIView):



    '''Takes phone and email and creates a new user only if otp was verified 
    and only new phone can register
         {
        "email": "example@gmail.com",
        'phone":"+2348101464914",
        "otp" : "9400"
         }  

         return a status True if the request went well with detail of what happened
         retuen false if the process did not go well note and detail of what happened is attached to this request
    '''


    serializer_class = CreateUserSerializer
    test_param =openapi.Parameter("email",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    phone_param =openapi.Parameter("phone",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    otp_param =openapi.Parameter("otp",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' register and save a user',manual_parameters=[test_param,phone_param,otp_param],operation_description='Takes phone and email and creates a new user only if otp was verified and only new phone can register'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        email = request.data.get('email', False)
        otp = request.data.get('otp', False)

        if phone and email:
            phone = str(phone)
            user = User.objects.filter(phone__iexact = phone)
            user_email = User.objects.filter(email = email)
            if user.exists():
                return Response({'status': False, 'detail': 'Phone Number already have account associated. Kindly sign in'})
            elif user_email.exists():
                return Response({'status': False, 'detail': 'Email already have account associated. Kindly sign in'})
 
            else:
                old = PhoneOTP.objects.filter(phone__iexact = phone)
                if old.exists():
                    sotp=PhoneOTP.objects.get(phone__iexact = phone)
                    save_otp=sotp.otp
                    print(save_otp)
                    if otp==save_otp:
                        Temp_data = {'phone': phone, 'email': email}

                        serializer = CreateUserSerializer(data=Temp_data)
                        serializer.is_valid(raise_exception=True)
                        user = serializer.save()
                        user.save()
                        save_otps = User.objects.get(phone=phone)
                        save_otps.otp=save_otp
                        save_otps.save()
                        return Response({
                            'status' : True, 
                            'detail' : 'Congrts, user has been created successfully.'
                        })
                    else:
                        return Response({

                            'status': False,
                            'detail': 'invalid otp'

                        })
                else:
                    return Response({
                    'status' : False,
                    'detail' : 'Phone number not recognised. Kindly request a new otp with this number'
                })
                    

        else:
            return Response({
                'status' : False,
                'detail' : 'Either phone number or email was not recieved in Post request'
            })



class AdminRegister(GenericAPIView):



    '''Takes phone and email and creates a new user only if otp was verified 
    and only new phone can register
         {
        
        'phone":"+2348101464914",
        "password" : "9400"
         }  

         return a status True if the request went well with detail of what happened
         retuen false if the process did not go well note and detail of what happened is attached to this request
    '''


    serializer_class = CreateAdminUserSerializer

    phone_param =openapi.Parameter("phone",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    otp_param =openapi.Parameter("password",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' register an admin user',manual_parameters=[phone_param,otp_param],operation_description='Takes phone and email and creates a new user only if otp was verified and only new phone can register'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        password = request.data.get('password', False)

        if phone:
            phone = str(phone)
            user = User.objects.filter(phone__iexact = phone)
        
            if user.exists():
                return Response({'status': False, 'detail': 'Phone Number already have account associated. Kindly sign in'})
            else:
                old = PhoneOTP.objects.filter(phone__iexact = phone)
                Temp_data = {'phone': phone, 'password': password}

                serializer = CreateAdminUserSerializer(data=Temp_data)
                serializer.is_valid(raise_exception=True)
                user = serializer.save()
                user.save()
                return Response({
                    'status' : True, 
                    'detail' : 'Congrts, user has been created successfully.'
                })

        else:
            return Response({
                'status' : False,
                'detail' : 'Either phone number or email was not recieved in Post request'
            })

class AdminOwnerInfo(GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    @swagger_auto_schema(operation_summary=' get rwquest collect all resturant owner that is in the database',operation_description='produce the total number of resturant owner in the database'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})

    def get(self,request):
        users = User.objects.all()

        k=[]
        count=0
        for user in users:
         
            try:
                owner= Ownerprofiles.objects.get(user=user)
                kd={
                    "id":owner.id,
                    'phone':user.phone,
                    "email":user.email,
                    'resturant_location':owner.resturant_location,
                    "resturant_name":owner.resturant_name,
                    
                }
                k.append(kd)
                count +=1
            except:
                pass
        return Response({'owner':k,'total number':count})

    phone_param =openapi.Parameter("id",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    otp_param =openapi.Parameter("resturant_name",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    otps_param =openapi.Parameter("resturant_location",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' patch rwquest update date of resturant owner that is in the database',manual_parameters=[phone_param,otp_param,otps_param],operation_description='update owneeer information in the database  note it is not compulsory you fill in the all param fill the ones that is needed'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})

    def patch(self,request):
        id= request.data.get('id')
        name = request.data.get('resturant_name',False)
        location = request.data.get('resturant_location',False)
        user = User.objects.get(id=id)
        try:
            owner=Ownerprofiles.objects.get(user=user)
        except:
            return Response({
            'status': False,'details':"account does not exist"
        })
        if name:
            owner.resturant_name=name
        if location:
            owner.resturant_location=location

        
        owner.save()
        
        return Response({
            'status': True,'details':"account succesfully edited"
        })    
    phone_param =openapi.Parameter("id",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' delete rwquest delete date of resturant owner that is in the database',manual_parameters=[phone_param,otp_param,otps_param],operation_description='delete owneeer information in the database  this use the id to know or identify the owner to delete'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})

    def delete(self,request):
        id= request.data.get('id')
        user = User.objects.get(id=id)
        try:
            driver=Ownerprofiles.objects.get(user=user)
        except:
            return Response({
            'status': False,'details':"account does not exist"
        })
        driver.delete()
        user.delete()

        return Response({
            'status': True,'details':"account succesfully deleted"
        })

class AdminDriverInfo(GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    @swagger_auto_schema(operation_summary=' get request collect all driver that is in the database',operation_description='produce the total number of driver in the database'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})

    def get(self,request):
        users = User.objects.all()

        k=[]
        count=0
        for user in users:
            try:
                owner= Drivers.objects.get(user=user)
                kd={
                    "id":user.id,
                    'phone':user.phone,
                    "email":user.email,
                    "driver_number":owner.driver_number,
                    'first_name':owner.first_name,
                    "last_name":owner.last_name,
                    "email":owner.email,
                    "ssn":owner.ssn,
                    "vehicle_color":owner.vehicle.color,
                    "make":owner.vehicle.make,
                    'model':owner.vehicle.model,
                    "year":owner.vehicle.year,
                    
                }
                k.append(kd)
                count +=1
            except:
                pass
        return Response({'owner':k,'total':count})
    phone_param =openapi.Parameter("id",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' delete rwquest delete date of driver that is in the database',operation_description='delete driver information in the database by using the id given to know the driver to delete'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})

    def delete(self,request):
        id= request.data.get('id')
        user = User.objects.get(id=id)
        try:
            driver=Drivers.objects.get(user=user)
        except:
            return Response({
            'status': True,'details':"account does not exist"
        })
        driver.delete()
        user.delete()

        return Response({
            'status': True,'details':"account succesfully deleted"
        })


    phone_param =openapi.Parameter("id",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    otp_param =openapi.Parameter("first_name",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    otps_param =openapi.Parameter("last_name",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    middle_param =openapi.Parameter("state",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    ssn_param =openapi.Parameter("ssn",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    driver_param =openapi.Parameter("driver_number",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    state_param =openapi.Parameter("middle_name",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    @swagger_auto_schema(operation_summary=' patch rwquest update date of driver that is in the database',manual_parameters=[phone_param,otp_param,otps_param,driver_param,ssn_param,state_param,middle_param],operation_description='update driver information in the database  note it is not compulsory you fill in the all param fill the ones that is needed'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})

    def patch(self,request):
        id= request.data.get('id')
        first = request.data.get('first_name',False)
        last = request.data.get('last_name',False)
        middle = request.data.get('middle_name',False)
        ssn = request.data.get('ssn',False)
        driver_number = request.data.get('driver_number',False)
        state = request.data.get('state',False)
        user = User.objects.get(id=id)
        try:
            driver=Drivers.objects.get(user=user)
        except:
            return Response({
            'status': False,'details':"account does not exist"
        })
        if ssn:
            driver.ssn=ssn
        if state:
            driver.state=state
        if driver_number:
            driver.driver_number=driver_number
        if first:
            driver.first_name=first
        if last:
            driver.last_name=last
        if middle:
            driver.middle_name=middle
        
        driver.save()
        
        return Response({
            'status': True,'details':"account succesfully edited"
        })   

class Adminjob(GenericAPIView):

    
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    @swagger_auto_schema(operation_summary=' get request collect all job that is in the database',operation_description='produce the total number of job in the database'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})

    def get(self,request):
        
        jobs = JobRequest.objects.all()

        k=[]
        for job in jobs:
            try:
                owner= Ownerprofiles.objects.get(user=job.owner)
                kd={
                    "id":job.id,
                    "pickup_lat":job.pickup_lat,
                    "pickup_long":job.pickup_long,
                    "pickup_address":job.pickup_address,
                    "owner":owner.resturant_name,
                    "loaction":owner.resturant_location,
                    "status":job.status,
                    "driver":job.carier.first_name + job.carier.last_name,
                    "create_at":job.create_at

                }
                k.append(kd)
            except:
                pass
        return Response({'job':k})
    id_param =openapi.Parameter("id",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    status_param =openapi.Parameter("status",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    @swagger_auto_schema(operation_summary=' patch rwquest update status of job that is in the database',manual_parameters=[id_param,status_param],operation_description='update status of job in the database '
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})

    def patch(self,request):
        id = request.data.get('id')
        try:
            job = JobRequest.objects.get(id=id)
        except:
            return Response({
            'status': True,'details':"job does not exist"
        })

        status = request.data.get('status')
        job.status=status
        job.save()
        return Response({
            'status': True,'details':"job status changed"
        })
    phone_param =openapi.Parameter("id",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' delete rwquest delete date of job that is in the database',operation_description='delete job information in the database by using the id given to know the job to delete'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})

    def delete(self,request):
        id = request.data.get('id')
        try:
            job = JobRequest.objects.get(id=id)
        except:
            return Response({
            'status': True,'details':"job does not exist"
        })

        job.delete()
        return Response({
            'status': True,'details':"job deleted"
        })



class ownerRegister(GenericAPIView):



    '''Takes phone and creates a new owner only if otp was verified 
    and only new phone can register
         {
        'phone":"+2348101464914",
        "otp" : "9400"
         }  

         return a status True if the request went well with detail of what happened
         retuen false if the process did not go well note and detail of what happened is attached to this request
    '''


    serializer_class = CreateUserSerializer
    phone_param =openapi.Parameter("phone",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    otp_param =openapi.Parameter("otp",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' register and save a user',manual_parameters=[phone_param,otp_param],operation_description='Takes phone and email and creates a new user only if otp was verified and only new phone can register'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp = request.data.get('otp', False)

        if phone :
            phone = str(phone)
            user = User.objects.filter(phone__iexact = phone)
            if user.exists():
                return Response({'status': False, 'detail': 'Phone Number already have account associated. Kindly sign in'})

 
            else:
                old = PhoneOTP.objects.filter(phone__iexact = phone)
                if old.exists():
                    sotp=PhoneOTP.objects.get(phone__iexact = phone)
                    save_otp=sotp.otp
                    print(save_otp)
                    if otp==save_otp:
                        Temp_data = {'phone': phone, 'email': 'email@gmail.com'}

                        serializer = CreateUserSerializer(data=Temp_data)
                        serializer.is_valid(raise_exception=True)
                        user = serializer.save()
                        user.save()
                        save_otps = User.objects.get(phone=phone)
                        save_otps.otp=save_otp
                        save_otps.save()
                        return Response({
                            'status' : True, 
                            'detail' : 'Congrts, user has been created successfully.'
                        })
                    else:
                        return Response({

                            'status': False,
                            'detail': 'invalid otp'

                        })
                else:
                    return Response({
                    'status' : False,
                    'detail' : 'Phone number not recognised. Kindly request a new otp with this number'
                })
                    

        else:
            return Response({
                'status' : False,
                'detail' : 'Either phone number or email was not recieved in Post request'
            })

class ValidateLogin(GenericAPIView):


    phone_param =openapi.Parameter("phone",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' validate user existence',manual_parameters=[phone_param],operation_description='    This class view takes phone number in which user want to login withand validate it if it exist in the database'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact = phone)
            if not user.exists():
                return Response({'status': False, 'detail': 'Phone Number does not exist please kindly signup'})
                 # logic to send the otp and store the phone number and that otp in table. 
            else:
                otp = 1234#otp_generator()
                try:
                    send_otp=1234#MessageHandler(phone,otp).send_otp()
                except:
                    return Response({'status': False, 'detail': ' unable to send otp check the number again '})
                print(phone, otp)
                if send_otp:
                    otp = str(otp)
                    old = User.objects.get(phone__iexact = phone)
                    old.otp=otp
                    print(old.otp)
                    old.save()
                else:
                    return Response({
                                'status': False, 'detail' : "OTP sending error. Please try after some time."
                            })

                return Response({
                    'status': True, 'detail': 'Otp has been sent successfully.'
                })
        else:
            return Response({
                'status': False, 'detail' : "I haven't received any phone number. Please do a POST request."
            })

class LoginAPI(KnoxLoginView,GenericAPIView):

    serializer_class = LoginUserSerializer
    permission_classes = (permissions.AllowAny,)


    phone_param =openapi.Parameter("phone",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    otp_param =openapi.Parameter("otp",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' validate user existence',manual_parameters=[phone_param,otp_param],operation_description='    this api takes the user phone number and otp it check if the otp is correct if not send a false status'
    ,responses={200:'successfull','response description':" return the auth token"})

    def post(self, request, format=None):
        phone = request.data.get('phone')
        otp = request.data.get('otp')
        old = User.objects.get(phone = phone)
        if otp==old.otp:
            pass
        else:
            return Response({
                'status': False, 'detail': 'invalid otp.'
            })

        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user.last_login is None :
            user.first_login = True
            user.save()
            
        elif user.first_login:
            user.first_login = False
            user.save()
            
        login(request, user,backend='api.auth_backend.PasswordlessAuthBackend2')
        return super().post(request, format=None)
        
class AdminLoginAPI(KnoxLoginView,GenericAPIView):

    serializer_class = LoginUserSerializer
    permission_classes = (permissions.AllowAny,)


    phone_param =openapi.Parameter("phone",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    otp_param =openapi.Parameter("password",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' login admin user',manual_parameters=[phone_param,otp_param],operation_description='    this api takes the user phone number and password to login'
    ,responses={200:'successfull','response description':" return the auth token"})

    def post(self, request, format=None):
        phone = request.data.get('phone')
        password = request.data.get('password')
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
            
        login(request, user)
        return super().post(request, format=None)


class ValidateDriver(GenericAPIView):

    serializer_class = DriverSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    test_param =openapi.Parameter("email",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    last =openapi.Parameter("last_name",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    first =openapi.Parameter("first_name",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    state =openapi.Parameter("state",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    middle =openapi.Parameter("middle_name",openapi.IN_QUERY,type=openapi.TYPE_STRING)
    phone_param =openapi.Parameter("ssn",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    otp_param =openapi.Parameter("driver_number",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' background check api',manual_parameters=[test_param,phone_param,otp_param,last,middle,state,first],operation_description='    this api post check the driver information and create it if it is correct'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})


    def post(self, request, format=None):
        email = request.user.email
        print(email)
        first = request.data.get('first_name')
        last = request.data.get('last_name')
        middle = request.data.get('middle_name')
        ssn = request.data.get('ssn')
        driver_number = request.data.get('driver_number')
        state = request.data.get('state')
        user=request.user.id
        print(user)
        validate_Driver = Drivers.objects.filter(user=user).exists()
        if validate_Driver:
            return Response({
                'status': False, "detail":"Driver already exist"
            })
        else:
            Temp_data = {'user':user,'state':state,'last_name':last,"first_name":first,"middle_name":middle,"ssn":ssn, 'email': email,"driver_number":driver_number }
            serializer = DriverSerializer(data=Temp_data)
            serializer.is_valid(raise_exception=True)
            driver=serializer.save()
            driver.save()
            return Response({
                        'status': True, 'detail': 'Driver successfully.'
                    })

    """
        this api post check the driver information 
        and create it
        if it is correct
        """
    def get(self,request):
        user= request.user
        try:
            job= Drivers.objects.filter(user=user)
        except Drivers.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(
                        DriverSerializer(job,many=True).data
                    )

        
class Profile(GenericAPIView):
 
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    
    @swagger_auto_schema(operation_summary=' getting of driver api',operation_description=' this api GET the driver profile '
    ,responses={200:'successfull',  "id": 'string',
                "driver_number":'string',
                'first_name':'string',
                "last_name":'string',
                "email":'string',
                "ssn":'string',
                "vehicle_color":'string',
                "make":'string',
                'model':'string',
                "year":'string'})

    def get(self,request):
        user= request.user
        try:
           job= Drivers.objects.filter(user=user)
        except Drivers.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        ve= Drivers.objects.get(user=user)
        print(ve.vehicle)
        try:
            veh= Vehicle.objects.filter(id=ve.vehicle.id)
            print(veh)
        except Vehicle.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        k=[]
        kd= {
                "id":ve.id,
                "driver_number":ve.driver_number,
                'first_name':ve.first_name,
                "last_name":ve.last_name,
                "email":ve.email,
                "ssn":ve.ssn,
                "vehicle_color":ve.vehicle.color,
                "make":ve.vehicle.make,
                'model':ve.vehicle.model,
                "year":ve.vehicle.year,
                "phone": request.user.phone


            }
        k.append(kd)
        return Response({'status': True,'driver':kd})

    def patch(self,request):
        driver= Drivers.objects.get(user=request.user)
        if request.FILES.get('image'):
            image = request.FILES.get('image')
            driver.image=image
        if request.data.get('email'):
            email = request.data.get('email')
            driver.email= email
        try:
            driver.save()
        except:
                return Response({
                    'status': False, 'detail': 'something when wrong unable to save'
                })
        

        return Response({
                        'status': True, 'detail': 'profile successfully updated.'
                    })
        

        


class ValidateVehicle(GenericAPIView):
    '''
    this api check the vehincle info and save it
       {
        "model": "example",
        'year":"2033",
        "color" : "red",
        "make":"tesla"
         }  

         return a status True if the request went well with detail of what happened
         retuen false if the process did not go well note and detail of what happened is attached to this request
    '''



    serializer_class = VehicleSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
 

    def post(self, request, format=None):
        make = request.data.get('make')
        year = request.data.get('year')
        model = request.data.get('model')
        color =request.data.get('color')
        print(color)
        driver = Drivers.objects.get(user=request.user)
        if driver.vehicle is not None:
            return Response({
                'status': False, "detail":"VEhicle already exist"
            })
        else:
            Temp_data = {'make': make,'color': color,'model': model, 'year': year }
            serializer = VehicleSerializer(data=Temp_data)
            serializer.is_valid(raise_exception=True)
            vehicle=serializer.save()
            vehicle.save()
            driver.vehicle=vehicle
            driver.save()
            return Response({
                        'status': True, 'detail': 'Vehicle successfully added.'
                    })

class driverlocation(GenericAPIView):



    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
 
    phone_param =openapi.Parameter("lat",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    otp_param =openapi.Parameter("long",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' driver location api',manual_parameters=[phone_param,otp_param],operation_description='    this api update the driver current location'
    ,responses={200:'successfull','response description':""" 'status': True, 'detail': 'updated driver location api.'"""})


    def patch(self, request, format=None):
        lat = request.data.get('lat')
        long = request.data.get('long')
        driver = Drivers.objects.get(user=request.user)
        driver.driver_lat=lat
        driver.driver_long=long
        driver.save()
        return Response({
                        'status': True, 'detail': 'updated driver locationapi.'
                    })

class driveronline(GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    otp_param =openapi.Parameter("online",openapi.IN_QUERY,type=openapi.TYPE_BOOLEAN)
    @swagger_auto_schema(operation_summary=' driver online state api',manual_parameters=[otp_param],operation_description="""this api update the driver ONLINE STATUS  {"online":"true"} """
    ,responses={200:'successfull','response description':"""       'status': True, 'detail': 'online profile updated.''"""})


    def patch(self, request, format=None):
        lat = request.data.get('online')
        driver = Drivers.objects.get(user=request.user)
        if str(lat) == "true":
            driver.online= True
        else:
            driver.online=False
        driver.save()
        return Response({
                        'status': True, 'detail': 'online profile updated.'
                    })



class Validateowner(GenericAPIView):
    """
    this api create a database for the owner with he or her resturant information
    """
    serializer_class = OwnerSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    phone_param =openapi.Parameter("resturant_name",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    phones_param =openapi.Parameter("resturant_location",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    otp_param =openapi.Parameter("name",openapi.IN_QUERY,type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(operation_summary=' create owner profile',manual_parameters=[phone_param,phones_param,otp_param],operation_description='    this api create a database for the owner with he or her resturant information'
    ,responses={200:'successfull','response description':" return the description details"})
    def post(self, request, format=None):
        email = request.user.email
        print(email)
        name = request.data.get('name')
        resturant_name = request.data.get('resturant_name')
        resturant_location = request.data.get('resturant_location')
        user=request.user.id
        print(user)
        validate_owner = Ownerprofiles.objects.filter(user=user).exists()
        if validate_owner:
            return Response({
                'status': False, "detail":"your infromation is already taken"
            })
        else:
            Temp_data = {'user':user,'name':name,'resturant_name':resturant_name,"resturant_location":resturant_location,'email': email }
            serializer = OwnerSerializer(data=Temp_data)
            serializer.is_valid(raise_exception=True)
            driver=serializer.save()
            driver.save()
            return Response({
                        'status': True, 'detail': 'owner info added successfully.'
                    })

class Createjob(ListCreateAPIView):
    '''
    this api is used to create a food request 
    '''
    serializer_class = JobRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    @swagger_auto_schema(operation_summary=' resturant sending food',operation_description="    this api is used to create a food request ",responses={200:'successfull',  "id": 'string',
                "pickup_lat":'float',
                'pickup_long ':'float',
                'driver_id':"string"
                })
    
    def post(self, request,format=None):
        driver_id =request.data.get("driver_id")
        driver= Drivers.objects.get(id= driver_id)
        pickup_lat= request.data.get('pickup_lat')
        pickup_long = request.data.get("pickup_long")

        delivery_address= 0
        delivery_lat = 0
        delivery_long = 0
        try:
            pickup_address= request.user.ownerprofiles.resturant_location
            resturant_name = request.user.ownerprofiles.resturant_name
        except:
            return Response({
                    'status': False, 'detail': 'Request denied you are not a resturant.'
                })
        owner=request.user
        temp_data = {'owner': owner.id,'pickup_address':pickup_address,'pickup_lat':pickup_lat,'delivery_address':delivery_address,
        'delivery_lat':delivery_lat,'delivery_long':delivery_long,'resturant_name':resturant_name,
        'pickup_long':pickup_long,'carier':driver.id
        }
        serializer = JobRequestSerializer(data=temp_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        drivernotice= Notice(user=driver.user,last_notice=f" new delivery request from {pickup_address}")
        drivernotice.save()
        ownernotice= Notice(user=request.user,last_notice=f" delivery request sent to {driver.first_name} {driver.last_name}")
        ownernotice.save()
        comfirmjob=JobRequest.objects.filter(owner=owner).last()
        driverjob=DriverRequest(carier=driver,jobrequest=comfirmjob)
        driverjob.save()
        return Response({
                    'status': True, 'detail': 'Request succesfully created.'
                })
    @swagger_auto_schema(operation_summary=' request for for created order',operation_description="result of all created order that was rejected by driver",responses={200:'successfull','description':"result of all created order that was rejected by driver"})
    def get(self,request):
        user= request.user
        try:
            jobs= JobRequest.objects.filter(owner=user.id)
        except JobRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        k=[]
        for job in jobs:
            driver=job.carier.id
            drive=Drivers.objects.get(id=driver)
            try:
                imag=drive.image.url
            except:
                imag=''
            kd= {
                "id":job.id,
                "status":job.status,
                "first_name":drive.first_name,
                "last_name":drive.last_name,
                "picture":imag
            }
            k.append(kd)
        
        return Response({'status': True,'job':list(k)})
        
        
class nearbydriver(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    def get(self,request,format=None):
        user= request.user
        drivers = Drivers.objects.filter(online=True)
        driver=drivers.values()
        return Response({
                     'nearbydriver':driver}
                    ) 


class activerequest(GenericAPIView):


    serializer_class = RequestSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    @swagger_auto_schema(operation_summary=' resturant sending food',operation_description="""  api  for accepting the driver has picked up the order which takes id and status
    
    example 

    {"id" : "93847774774848",
        "status": "pending"
    }
    
    note that the id is gotten from the get request
    """ ,responses={200:'successfull',}
     
    )
    def patch(self,request,format=None):
        user= request.user
        id= request.data.get('id')
        
        job= JobRequest.objects.get(id=id)
        tempdata = {'status':'pending'}
        serializer = RequestSerializer(job,data=tempdata,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
                    'status': True, 'detail': 'Request succesfully changed to pending.'
                })


    @swagger_auto_schema(operation_summary=' show accepted job from driver',operation_description=" show all accepted job "  ,responses={200:'successfull',}
     
    )
    def get(self,request,format=None):
        user= request.user
        try:
            job= JobRequest.objects.filter(owner=user.id,status='active')
        except JobRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(
                        RequestSerializer(job,many=True).data
                    ) 

class Deliveredrequest(GenericAPIView):


    serializer_class = RequestSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    @swagger_auto_schema(operation_summary='delivered order by driver',operation_description="""  api  for accepting the driver has delivered the order which takes id and status
    
    {"id" : "93847774774848",
        "status": "completed"
    }
    
    note that the id is gotten from the get request
    """ ,responses={200:'successfull',}
     
    )
    def patch(self,request,format=None):
        user= request.user
        id= request.data.get('id')
        
        job= JobRequest.objects.get(id=id)
        tempdata = {'status':'completed'}
        serializer = RequestSerializer(job,data=tempdata,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
                    'status': True, 'detail': 'Request succesfully changed to completed.'
                })


    @swagger_auto_schema(operation_summary=' show delivered job from driver',operation_description=" show all delivered job "  ,responses={200:'successfull',}
     
    )

    def get(self,request,format=None):
        user= request.user
        try:
            job= JobRequest.objects.filter(owner=user.id,status='delivered')
        except JobRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(
                        RequestSerializer(job,many=True).data
                    ) 

class Completedrequest(GenericAPIView):


    serializer_class = RequestSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    @swagger_auto_schema(operation_summary='rate delivered order by driver',operation_description="""  api  for rating the driver please not this api is under development
    
    {"id" : "93847774774848",
        "comment": "comment"
        "rating" :"3"
    }
    
    note that the id is gotten from the get request
    """ ,responses={200:'successfull',}
     
    )
    def patch(self,request,format=None):
        user= request.user
        id= request.data.get('id')
        ratings= request.data.get('rating')
        comment= request.data.get('comment')

        job= JobRequest.objects.get(id=id)
        carier = job.carier
        rating =Rating(jobrequest=job,carier=carier,rating=ratings,comment=comment)
        rating.save()
        carier_id=carier.id
        driver= Drivers.objects.get(id=carier_id)
        totalrate= float((float(driver.rating) + int(ratings))/2)
        totalsuccess= int(int(driver.totaldelivery) + 1)
        driver.rating=totalrate
        driver.totaldelivery=totalsuccess
        driver.save()        
        tempdata = {'status':'completed'}
        serializer = RequestSerializer(job,data=tempdata,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
                    'status': True, 'detail': 'Request succesfully changed to completed.'
                })


    @swagger_auto_schema(operation_summary=' show completed job from driver',operation_description=" show all completed job "  ,responses={200:'successfull',}
     
    )

    def get(self,request,format=None):
        user= request.user
        try:
            job= JobRequest.objects.filter(owner=user.id,status='completed')
        except JobRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(
                        RequestSerializer(job,many=True).data
                    ) 

    def calculaterating(self):
        pass

class OwnerEmail(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    '''take in email of owner
         {
        'email":"jjk@gmail.com",

         }  

         return a status True if the request went well with detail of what happened
         retuen false if the process did not go well note and detail of what happened is attached to this request
    '''


    serializer_class = CreateUserSerializer
    phone_param =openapi.Parameter("email",openapi.IN_QUERY,type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_summary=' owner email uppdate',manual_parameters=[phone_param],operation_description='take in email of owneremail:jjk@gmail.com,'
    ,responses={200:'successfull','response description':"return a status True if the request went well with detail of what happenedretuen false if the process did not go well note and detail of what happened is attached to this request",'status':"true",'detail':'infomation of what happened'})

    def patch(self,request,format=None):
        user= request.user
        email= request.data.get('email')
        user_email = User.objects.filter(email = email)
        if user_email.exists():
            return Response({'status': False, 'detail': 'Email already have account associated. Kindly sign in'})
        user.email=email
        user.save()
        return Response({'status': True, 'detail': 'Email succesfull added'})




class DriverRequests(GenericAPIView):
    '''
    use the get request to get the driver request

    use the patch request to accept or declined the request from the owber
    the id pass in the patch is from the id that was gotten from the get request

    to accept
    {
        id:"48848489494949"
        status:"Accept"
    }
    to declined

        {
        id:"48848489494949"
        status:"Declined"
    }

    to complete

        {
        id:"48848489494949"
        status:"Completed"
    }
    '''

    serializer_class = DriverSerializers
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    def get(self,request,format=None):
        user = request.user
        status = 'Request'
        # job_request= JobRequest.objects.get(id=id)
        driver_id = Drivers.objects.get(user = user)
        driverrequest= DriverRequest.objects.filter(status=status,carier=driver_id.id)
        # job = JobRequest.objects.filter(id=driverrequest.jobrequest)
        # print(driver_id)

        # print(driverrequest)
        # k = job.values().update("request_id":driverrequest.id)
        k=[]
        for l in driverrequest:
            job=JobRequest.objects.get(id=l.jobrequest.id)
            kd= {
                "id":l.id,
                "status":l.status,
                'resturant_name':job.resturant_name,
                "delivery_address":job.pickup_address,
                "resturant_lat":job.pickup_lat,
                "resturant_long":job.pickup_long
            }
            k.append(kd)
        

        return Response({'status': True,'job':list(k)})

    def patch(self,request,format=None):
        user= request.user
        id= request.data.get('id')
        status= request.data.get('status')
        

        driverrequest= DriverRequest.objects.get(id=id)
        job= JobRequest.objects.get(id=driverrequest.jobrequest.id)
        if status == 'Accept':
            job.status='active'
            job.save()
            tempdata = {'status':'Accept'}
            serializer = DriverSerializers(driverrequest,data=tempdata,partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            ownernotice= Notice(user=request.job.owner,last_notice=f" delivery request accepted by {driverrequest.first_name} {driverrequest.last_name}")
            ownernotice.save()
            return Response({
                        'status': True, 'detail': 'Request succesfully changed to accpeted.'
                    })
        elif status=='Completed':
            job.status='delivered'
            job.save()
            tempdata = {'status':'Completed'}
            serializer = DriverSerializers(driverrequest,data=tempdata,partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            ownernotice= Notice(user=request.job.owner,last_notice=f" delivery request completed by {driverrequest.first_name} {driverrequest.last_name}")
            ownernotice.save()
            return Response({
                        'status': True, 'detail': 'Request succesfully changed to Completed.'
                    })
        elif status=='Declined':
            job.status='cancelled'
            job.save()
            tempdata = {'status':'Declined'}
            serializer = DriverSerializers(driverrequest,data=tempdata,partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            ownernotice= Notice(user=request.job.owner,last_notice=f" delivery request Declined by {driverrequest.first_name} {driverrequest.last_name}")
            ownernotice.save()
            return Response({
                        'status': True, 'detail': 'Request succesfully changed to Declined.'
                    })
        else:
            return Response({
                        'status': False, 'detail': 'Status not given'
                    })

class DriverRequestsCompleted(GenericAPIView):
    '''
    api for get the driver completed job 
   
    
    '''

    serializer_class = DriverSerializers
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    
    def get(self,request,format=None):
        user = request.user
        status = 'Completed'
        # job_request= JobRequest.objects.get(id=id)
        driver_id = Drivers.objects.get(user = user)
        driverrequest= DriverRequest.objects.filter(status=status)
        
        # job = JobRequest.objects.filter(id=driverrequest.jobrequest)
        # print(driver_id)

        # print(driverrequest)
        # k = job.values().update("request_id":driverrequest.id)
        k=[]
        for l in driverrequest:
            job=JobRequest.objects.get(id=l.jobrequest.id)
            kd= {
                "id":l.id,
                "status":l.status,
                'resturant_name':job.resturant_name,
                "delivery_address":job.delivery_address

            }
            k.append(kd)
        

        return Response({'status': True,'job':list(k)})
        # dns1.p02.nsone.net

class Notification(GenericAPIView):
    '''
    api for get the driver completed job 
   
    
    '''
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    def get(self,request,format=None):
        user = request.user
        try:

            note = Notice.objects.filter(user=user).last()
            np=note.last_notice

        except:
            return Response({'status': False,'detail':"notification not available"})            
        return Response({'status': True,'notice':note.last_notice,'timecreated':note.create_at})


class AllNotification(GenericAPIView):
    '''
    api for get the driver completed job 
   
    
    '''
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    def get(self,request,format=None):
        user = request.user
        try:

            note = Notice.objects.filter(user=user).values()

        except:
            return Response({'status': False,'detail':"notification not available"})            
        return Response({'status': True,'notice':note})


class Resturantprofile(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    '''take in profile of owner
         {
        'email":"jjk@gmail.com",
        'name':"resturant name'
        'location':"resturant location'

         }  

         return a status True if the request went well with detail of what happened
         retuen false if the process did not go well note and detail of what happened is attached to this request
    '''

    def patch(self,request,format=None):
        user= request.user
        email= request.data.get('email',False)
        name= request.data.get('name',False)
        location= request.data.get('location',False)
        image = request.files.get('image',False)
        owner=Ownerprofiles.objects.get(user=user)
        if email:
            owner.email=email
        elif name:
            owner.resturant_name=name
        elif location:
            owner.resturant_location=location
        elif image:
            owner.image=image
        else:
            return Response({'status': False, 'detail': 'no information was passed'})
        owner.save()
        return Response({'status': True, 'detail': 'information succesfull added'})
    def get(self,request):
        user=request.user
        owner=Ownerprofiles.objects.get(user=user)
        return Response({'status': True, 'email': owner.email,'phone':request.user.phone,'location':owner.resturant_location,'name':owner.resturant_name})


