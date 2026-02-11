from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='groups')
router.register(r'media', MediaGroupViewSet, basename='media')
router.register(r'group-home-publication', PublicationByGroupViewSet, basename='group-publication')


urlpatterns = [
    path('directions/',direction_list_list),
    path('group-home/',home_group_list),
    path('group-news/', NewshomeView.as_view()),
    path('group-publication/',PublicationView.as_view()),
    path('group-conferinsia/',ConferensiaViews.as_view()),
    path('group-members/', MemberByGroupView.as_view()),
    path('group-interest/', InterestView.as_view()),
    path("projects/", ProjectsListAPIView.as_view()),

    path('',include(router.urls)),
]