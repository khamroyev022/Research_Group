from django.urls import path
from .views import *

urlpatterns = [
    path('home/',group_list_api)
]