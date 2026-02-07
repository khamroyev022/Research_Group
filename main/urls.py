from django.urls import path
from .views import *

urlpatterns = [
    path('group/',group_list_api),
    path('direction-list/',direction_list_list)
]