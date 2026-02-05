import django_filters
from main.models import Member

class MemberFilter(django_filters.FilterSet):
    group_name = django_filters.CharFilter(
        field_name='group__group__name',   # <-- TO‘G‘RI
        lookup_expr='icontains'
    )

    class Meta:
        model = Member
        fields = ['group']  # faqat Member model fieldlari
