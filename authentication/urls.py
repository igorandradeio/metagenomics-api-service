from django.contrib import admin
from django.urls import path

from . import views


app_name = "authentication"

urlpatterns = [
    path("register/", views.register),
    path("login/", views.login),
    path("logout/", views.logout),
    path("me/", views.me),
]
