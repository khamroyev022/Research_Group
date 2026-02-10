from django.template.defaultfilters import title
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .Pagnitions import DefaultPagination
from .serializer import *
from rest_framework import status
from  rest_framework.viewsets import ReadOnlyModelViewSet

@api_view(["GET"])
@permission_classes([AllowAny])
def direction_list_list(request):
    lang = request.headers.get("Accept-Language", "uz")
    qs = Direction.objects.all().prefetch_related("details")
    ser = DirectionSerializer(qs, many=True, context={"language": lang, "request": request})
    return Response({
        "language": lang,
        "data": ser.data
    }, status=status.HTTP_200_OK)



class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all().select_related("direction").prefetch_related("details")
    serializer_class = GroupSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["direction"]





class MediaGroupViewSet(ReadOnlyModelViewSet):
    queryset = GroupMedia.objects.all().select_related("group").prefetch_related("details")
    serializer_class = MediaSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["group"]
    lookup_field = "slug"


@api_view(["GET"])
@permission_classes([AllowAny])
def home_group_list(request):
    group_id = request.query_params.get("group_id")
    lang = request.headers.get("Accept-Language", "uz")

    slider_qs = SliderGroup.objects.all().select_related("group")
    if group_id:
        group_id = group_id.strip().rstrip("/")
        slider_qs = slider_qs.filter(group_id=group_id)

    slider_ser = SlidergroupSerializer(slider_qs, many=True, context={"request": request})

    # Achivment
    achivment_obj = Achivment.objects.all()
    if group_id:
        achivment_obj = achivment_obj.filter(group_id=group_id)
    achivment_obj = achivment_obj.first()

    ach_data = None
    if achivment_obj:
        tr = get_fallback_detail(achivment_obj.achivment, lang)
        ach_data = {
            "id": achivment_obj.id,
            "image": request.build_absolute_uri(achivment_obj.image.url) if achivment_obj.image else None,
            "created_at": achivment_obj.created_at,
            "title": tr.title if tr else None,
            "slug": tr.slug if tr else None
        }

    # Partner
    partner_obj = Partnership.objects.all()
    if group_id:
        partner_obj = partner_obj.filter(group_id=group_id)
    partner_obj = partner_obj.first()

    partner_data = None
    if partner_obj:
        tg = get_fallback_detail(partner_obj.partnereship, lang)
        partner_data = {
            "id": partner_obj.id,
            "image": request.build_absolute_uri(partner_obj.image.url) if partner_obj.image else None,
            "created_at": partner_obj.created_at,
            "title": tg.title if tg else None,
            "slug": tg.slug if tg else None
        }
    # Student
    student_obj = ReserchStudent.objects.all()
    if group_id:
        student_obj = student_obj.filter(group_id=group_id)
    student_obj = student_obj.first()

    student_data = None
    if student_obj:
        tg = get_fallback_detail(student_obj.reserchStudent, lang)
        student_data = {
            "id": student_obj.id,
            "image": student_obj.image.url if student_obj.image else None,
            "created_at": student_obj.created_at,
            "title": tg.title if tg else None,
        }
    #Resourse

    resours_obj = Resources.objects.all()
    if group_id:
        resours_obj = resours_obj.filter(group_id=group_id)

    resours_obj = resours_obj.first()

    resours_data = None
    if resours_obj:
        tr = get_fallback_detail(resours_obj.resources, lang)

        resours_data = {
            "id": resours_obj.id,
            "image": request.build_absolute_uri(resours_obj.image.url) if resours_obj.image else None,
            "created_at": resours_obj.created_at,
            "title": tr.title if tr else None,
            "slug": tr.slug if tr else None,
        }
    return Response({
        "group_id": group_id,
        "data": {
            "slider": slider_ser.data,
            "achivment": ach_data,
            "partnership": partner_data,
            "research-student": student_data,
            "resourses": resours_data,
        }
    }, status=status.HTTP_200_OK)








