from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import *

router = DefaultRouter()

router.register('directions', DirectionCRUDViews, basename='direction')
router.register('institutes',UniversityViews)
router.register('countries',CountryViewSet)
router.register('groups',GroupViewset)
router.register('members',MemberViewset)
router.register('publications',PublicationViewSet)
router.register('publishers',PublishViewset)
router.register('projects',ProjectsViewSet)
router.register('interests',InterestsViewSet)
router.register('achievements',AchivmentViewSet)
router.register('partnerships',PartnershipViewSet)
router.register('research-students',ReserchStudentViewSet)
router.register('resources',ResourcesViewSet)
router.register('news-activities',NewsActivitiesViewSet)
router.register('conferences-seminars',ConferencesSeminarsViewSet)
router.register('slider-groups',SliderGroupViewSet)
router.register('group-media',GroupMediaViewSet)
router.register('social-links',SosialLinkViewset)
urlpatterns =[
    path('login/',loginviews,),
    # path('register/',register,),
    path('groups/is-active/<uuid:group_id>', groupactiveviews),
    path('groups/is-active/<uuid:group_id>/', groupactiveviews),
    path("auth/forgot-password/", forgot_password),
    # path("auth/verify-reset-code/", verify_reset_code),
    path("auth/reset-password/", reset_password),
] + router.urls
