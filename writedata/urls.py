"""
URL configuration for postdata project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from writedata import views



urlpatterns = [
    
    path('api/energy/', views.AMIListCreate.as_view()), 
    path('api/login/', views.LoginView.as_view(), name = "login"),
    path('api/register/', views.RegisterView.as_view(), name = "register"),
    path('api/register_device/', views.DeviceListCreate.as_view(), name = "register_device"),
    path('api/update_device/', views.update_device, name = "update_device"),
    path('api/Unbind_device/', views.DeviceUnbind.as_view(),name='Unbind_device'),
    path('api/updatedata/', views.updatedata,name='updatedata'),
    path('api/deletealldata/', views.deleteall,name='deleteall'),

    path('api/device_tranfor/', views.DeviceranforListCreate.as_view(),name='device_tranfor'),
    path('api/update_qrid_of_deviceUuid/', views.update_qrid_of_deviceUuid,name='update_qrid_of_deviceUuid'),
    path('api/delete_qrid/', views.delete_qrid,name='delete_qrid'),
    

]
