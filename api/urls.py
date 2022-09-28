from django.urls import path
from . import views
from knox import views as knox_view

urlpatterns = [

    path('verifyinformation/',views.ValidatePhoneSendOTP.as_view(),name='otp' ),
    path('register/',views.Register.as_view(),name='signup' ),
    path('verifylogin/',views.ValidateLogin.as_view(),name='login' ),
    path('login/',views.LoginAPI.as_view(),name='login' ),
    path('logout/',knox_view.LogoutView.as_view(),name='logout'),
    path('driver/',views.ValidateDriver.as_view(),name='login' ),
    path('owner/',views.Validateowner.as_view(),name='login' ),
    path('vehiclecheck/',views.ValidateVehicle.as_view(),name='vehicle' ),


]
