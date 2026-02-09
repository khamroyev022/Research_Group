from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='groups')

urlpatterns = [
    path('directions/',direction_list_list),
    path('',include(router.urls)),
]