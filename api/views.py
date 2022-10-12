from functools import partial
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
from .models import Ownerprofiles, PhoneOTP, User,Drivers, Vehicle,JobRequest,DriverRequest
from .serializer import CreateUserSerializer, DriverSerializers,OwnerSerializer, LoginUserSerializer,DriverSerializer,VehicleSerializer,JobRequestSerializer,RequestSerializer,DriverSerializers
from .utils import otp_generator, password_generator, phone_validator


class ValidatePhoneSendOTP(GenericAPIView):
    '''
    This class view takes phone number and email and if it doesn't exists already then it sends otp for
    first coming phone numbers 
    
    pls note this api is the first api you call before register


    '''

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact = phone)
            if user.exists():
                return Response({'status': False, 'detail': 'Phone Number already exists'})
                 # logic to send the otp and store the phone number and that otp in table. 
            else:
                otp = otp_generator()
                send_otp=MessageHandler(phone,otp).send_otp()

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



    '''Takes phone and a email and creates a new user only if otp was verified and phone is new'''


    serializer_class = CreateUserSerializer
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
                        Temp_data = {'phone': phone, 'email': email }

                        serializer = CreateUserSerializer(data=Temp_data)
                        serializer.is_valid(raise_exception=True)
                        user = serializer.save()
                        user.save()
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
                        # return Response({
                        #     'status' : True, 
                        #     'detail' : 'Congrts, user has been created successfully.'
                        # })
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
    """
    This class view takes phone number in which user want to login with
    and validate it if it exist in the database

    if not it ask you to register

    else
     it  send an otp
    """

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact = phone)
            if not user.exists():
                return Response({'status': False, 'detail': 'Phone Number does not exist please kindly signup'})
                 # logic to send the otp and store the phone number and that otp in table. 
            else:
                otp = otp_generator()
                send_otp=MessageHandler(phone,otp).send_otp()
                print(phone, otp)
                if send_otp:
                    otp = str(otp)
                    old = User.objects.get(phone__iexact = phone)
                    old.otp=otp
                    print(old.otp)
                    old.save()
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

class LoginAPI(KnoxLoginView,GenericAPIView):

    """
    this api takes the user phone number and otp 
    it check if the otp is correct if not send a false status
    """
    serializer_class = LoginUserSerializer
    permission_classes = (permissions.AllowAny,)



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
        


class ValidateDriver(GenericAPIView):
    """
    this api post check the driver information 
    and create it
    if it is correct
    """
    serializer_class = DriverSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )



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

class ValidateVehicle(GenericAPIView):
    '''
    this api check the vehincle info and save it
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


class Validateowner(GenericAPIView):
    """
    this api create a database for the owner with he or her resturant information
    """
    serializer_class = OwnerSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )


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
    this api is used to create request of the resturant owner 
    '''
    serializer_class = JobRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    def post(self, request,format=None):
        pickup_lat= request.data.get('pickup_lat')
        pickup_long = request.data.get("pickup_long")
        delivery_address= request.data.get("delivery_address")
        delivery_lat = request.data.get("delivery_lat")
        delivery_long = request.data.get("delivery_long")
        pickup_address= request.data.get("pickup_address")
        resturant_name = request.data.get("resturant_name")
        owner=request.user
        temp_data = {'owner': owner.id,'pickup_address':pickup_address,'pickup_lat':pickup_lat,'delivery_address':delivery_address,
        'delivery_lat':delivery_lat,'delivery_long':delivery_long,'resturant_name':resturant_name,
        'pickup_long':pickup_long
        }
        serializer = JobRequestSerializer(data=temp_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
                    'status': True, 'detail': 'Request succesfully created.'
                })

    def get(self,request):
        user= request.user
        try:
            job= JobRequest.objects.filter(owner=user.id)
        except JobRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(
                        JobRequestSerializer(job,many=True).data
                    )
        
        




class activerequest(GenericAPIView):
    '''
    api for updating the request

    '''
    serializer_class = RequestSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

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
    '''S
    api for updating the request

    '''
    serializer_class = RequestSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

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



    def get(self,request,format=None):
        user= request.user
        try:
            job= JobRequest.objects.filter(owner=user.id,status='delivered')
        except JobRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(
                        RequestSerializer(job,many=True).data
                    ) 



class DriverRequests(GenericAPIView):
    '''
    api for updating the driver request
    '''

    serializer_class = (DriverSerializers,JobRequestSerializer)
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    def get(self,request,format=None):
        user = request.user
        status = request.data.get('status')
        # job_request= JobRequest.objects.get(id=id)
        driver_id = Drivers.objects.get(user = user)
        job = JobRequest.objects.filter(carier=driver_id)
        print(driver_id)
        driverrequest= DriverRequest.objects.filter(status=status)
        return Response(
                        DriverSerializers(driverrequest,many=True).data,
                   
                    ) 

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
            return Response({
                        'status': True, 'detail': 'Request succesfully changed to Completed.'
                    })
