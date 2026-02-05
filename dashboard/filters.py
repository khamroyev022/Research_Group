
import django_filters
from django.db import models

from main.models import *

class ProjectsFilter(django_filters.FilterSet):
    university_id = django_filters.UUIDFilter(field_name='sponsor_university_id')
    country_id = django_filters.UUIDFilter(field_name='sponsor_country_id')

    status = django_filters.BooleanFilter(field_name='status')

    start_from = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_to   = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')

    end_from = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_to   = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = Projects
        fields = ['status', 'sponsor_university', 'sponsor_country']

class MemberFilter(django_filters.FilterSet):
    group_id = django_filters.UUIDFilter(field_name='group_id')
    university_id = django_filters.UUIDFilter(field_name='university_id')

    status = django_filters.CharFilter(field_name='status')

    group_name = django_filters.CharFilter(
        field_name='group__group__name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Member
        fields = ['group', 'university', 'status']


class NewsActivitiesFilter(django_filters.FilterSet):
    group_name = django_filters.CharFilter(
        field_name='group__group__name',
        lookup_expr='icontains'
    )

    class Meta:
        model = NewsActivities
        fields = ['group']

class PublicationFilter(django_filters.FilterSet):
    group_id = django_filters.UUIDFilter(field_name='group_id')
    member_name = django_filters.CharFilter(
        field_name='member__group__group__name',
    )
    group_name = django_filters.CharFilter(
        field_name='group__group__name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Publication
        fields = ['group', 'publisher', 'featured',"member_name",]