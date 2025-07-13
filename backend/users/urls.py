from django.contrib import admin
from django.urls import path
from .views import register_cognito_user

urlpatterns = [
     path('register/', register_cognito_user),
     
]

