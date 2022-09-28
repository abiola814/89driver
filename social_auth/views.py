from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from knox.views import LoginView as KnoxLoginView
from .serializers import GoogleSocialAuthSerializer, TwitterAuthSerializer, FacebookSocialAuthSerializer
from rest_framework import generics, permissions, status
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

import requests
from django.contrib.auth import login


class GoogleSocialAuthView(GenericAPIView,KnoxLoginView):
    permission_classes = (permissions.AllowAny,)


    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        """

        POST with "auth_token"

        Send an idtoken as from google to get user information

        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        print(data)
        login(request,data,backend='api.auth_backend.PasswordlessAuthBackend')
        return super().post(request, format=None)


class FacebookSocialAuthView(GenericAPIView,KnoxLoginView):

    serializer_class = FacebookSocialAuthSerializer

    def post(self, request):
        """

        POST with "auth_token"

        Send an access token as from facebook to get user information

        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return Response(data, status=status.HTTP_200_OK)


class TwitterSocialAuthView(GenericAPIView,):
    serializer_class = TwitterAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
