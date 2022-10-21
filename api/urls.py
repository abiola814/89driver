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
    path('activerequest/',views.activerequest.as_view(),name='active' ),
    path('createjob/',views.Createjob.as_view(),name='job' ),
        path('driverrequest/',views.DriverRequests.as_view(),name='job' ),
                path('drivercompleted/',views.DriverRequestsCompleted.as_view(),name='job' ),
    path('driverprofile/',views.Profile.as_view(),name='job' ),

        path('deliveredrequest/',views.Deliveredrequest.as_view(),name='job' ),

]
