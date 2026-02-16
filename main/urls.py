from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter
from .serach_view import global_search


router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='groups')
router.register(r'media', MediaGroupViewSet, basename='media')
router.register(r'group-publications',PublicationViewSet, basename='group-home-publication')
router.register(r'group-news', NewsViewSet, basename='group-news')
router.register(r'group-projects', ProjectsViewSet, basename='group-projects')
router.register(r'group-conferences', ConferencesViewSet, basename='group-conferences')


urlpatterns = [
    path('directions/',direction_list_list),
    path('group-home/',home_group_list),
    path('group-members/', MemberByGroupView.as_view()),
    path('group-interest/', InterestView.as_view()),
    path('group-media/', MediaViews.as_view()),
    path('group-socials/',SocialLinkViewSet.as_view()),
    path('group-slider-details/',GlobalSlugAPIView.as_view()),
    path("members/create/", MemberCreateApi.as_view()),
    path("members/<slug:slug>/", MemberDetailView.as_view()),
    path("search/", global_search, name="global_search"),

    path('',include(router.urls)),
]