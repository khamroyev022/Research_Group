
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from dashboard.serializers.Interest_serializer import InterestsSerializer
from .Pagnitions import DefaultPagination,GroupPaginatsion,PublicationHome
from .serializer import *
from rest_framework import status
from  rest_framework.viewsets import ReadOnlyModelViewSet

def get_active_fallback_detail(qs, lang, default_lang="uz"):
    model = qs.model
    has_is_active = any(f.name == "is_active" for f in model._meta.fields)
    qs_active = qs.filter(is_active=True) if has_is_active else qs

    if lang:
        d = qs_active.filter(language=lang).first()
        if d:
            return d

    if default_lang and lang != default_lang:
        d = qs_active.filter(language=default_lang).first()
        if d:
            return d

    return qs_active.first() or qs.first()

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

    group_id_clean = None
    if group_id:
        group_id_clean = group_id.strip().rstrip("/")

    group_data = None
    if group_id_clean:
        group_obj = Group.objects.filter(id=group_id_clean).first()
        if group_obj:
            g_tr = get_active_fallback_detail(group_obj.details.all(), lang)
            group_data = {
                "id": str(group_obj.id),
                "name": g_tr.name if g_tr else None,
                "image": request.build_absolute_uri(group_obj.image.url) if group_obj.image else None,
                "created_at": group_obj.created,
            }

    # Slider
    slider_qs = SliderGroup.objects.all().select_related("group")
    if group_id_clean:
        slider_qs = slider_qs.filter(group_id=group_id_clean)

    slider_ser = SlidergroupSerializer(slider_qs, many=True, context={"request": request})

    # Achivment
    achivment_obj = Achivment.objects.all()
    if group_id_clean:
        achivment_obj = achivment_obj.filter(group_id=group_id_clean)
    achivment_obj = achivment_obj.first()

    ach_data = None
    if achivment_obj:
        tr = get_fallback_detail(achivment_obj.achivment, lang)
        ach_data = {
            "id": str(achivment_obj.id),
            "image": request.build_absolute_uri(achivment_obj.image.url) if achivment_obj.image else None,
            "created_at": achivment_obj.created_at,
            "title": tr.title if tr else None,
            "slug": tr.slug if tr else None
        }

    # Partner
    partner_obj = Partnership.objects.all()
    if group_id_clean:
        partner_obj = partner_obj.filter(group_id=group_id_clean)
    partner_obj = partner_obj.first()

    partner_data = None
    if partner_obj:
        tg = get_fallback_detail(partner_obj.partnereship, lang)
        partner_data = {
            "id": str(partner_obj.id),
            "image": request.build_absolute_uri(partner_obj.image.url) if partner_obj.image else None,
            "created_at": partner_obj.created_at,
            "title": tg.title if tg else None,
            "slug": tg.slug if tg else None
        }

    # Student
    student_obj = ReserchStudent.objects.all()
    if group_id_clean:
        student_obj = student_obj.filter(group_id=group_id_clean)
    student_obj = student_obj.first()

    student_data = None
    if student_obj:
        tg = get_fallback_detail(student_obj.reserchStudent, lang)
        student_data = {
            "id": str(student_obj.id),
            "image": request.build_absolute_uri(student_obj.image.url) if student_obj.image else None,  # ✅ absolute qildim
            "created_at": student_obj.created_at,
            "title": tg.title if tg else None,
        }

    # Resource
    resours_obj = Resources.objects.all()
    if group_id_clean:
        resours_obj = resours_obj.filter(group_id=group_id_clean)
    resours_obj = resours_obj.first()

    resours_data = None
    if resours_obj:
        tr = get_fallback_detail(resours_obj.resources, lang)
        resours_data = {
            "id": str(resours_obj.id),
            "image": request.build_absolute_uri(resours_obj.image.url) if resours_obj.image else None,
            "created_at": resours_obj.created_at,
            "title": tr.title if tr else None,
            "slug": tr.slug if tr else None,
        }

    return Response({
        "group_id": group_id_clean or "",
        "group": group_data,   # ✅ man
        "data": {
            "slider": slider_ser.data,
            "achievement": ach_data,
            "partnership": partner_data,
            "research-student": student_data,
            "resources": resours_data,
        }
    }, status=status.HTTP_200_OK)


class NewshomeView(APIView):
    permission_classes = [AllowAny]
    pagination_class = GroupPaginatsion

    def get(self, request):
        group_id = request.query_params.get("group_id")

        if not group_id:
            return Response({"error": "Parametr berish shart"}, status=400)

        group_id = group_id.strip().rstrip("/")

        qs = NewsActivities.objects.filter(group_id=group_id)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request, view=self)

        ser = NewSerializerHome(page, many=True, context={"request": request})
        return paginator.get_paginated_response(ser.data)

class PublicationView(APIView):
    permission_classes = [AllowAny]
    pagination_class = GroupPaginatsion

    def get(self, request):
        group_id = request.query_params.get("group_id")

        if not group_id:
            return Response({"error": "group_id param berilmadi"}, status=400)

        group_id = group_id.strip().rstrip("/")

        qs = Publication.objects.filter(group_id=group_id)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request, view=self)

        ser = PublicationSerializerhome(page, many=True, context={"request": request})
        return paginator.get_paginated_response(ser.data)

class ConferensiaViews(APIView):
    permission_classes = [AllowAny]
    pagination_class = GroupPaginatsion

    def get(self, request):
        group_id = request.query_params.get("group_id")
        if not group_id:
            return Response({"error": "group_id param berilmadi"}, status=400)

        group_id = group_id.strip().rstrip("/")
        qs = ConferencesSeminars.objects.filter(group_id=group_id)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request, view=self)

        ser = ConferensiahomeSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(ser.data)


class MemberByGroupView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        group_id = request.query_params.get("group_id")

        if not group_id:
            return Response(
                {"error": "group_id param berilmadi"},
                status=400
            )

        group_id = group_id.strip().rstrip("/")

        qs = Member.objects.filter(group_id=group_id) \
            .select_related("group", "country", "university") \
            .prefetch_related("details")

        serializer = MemberGetSerializer(
            qs,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)

class InterestView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        group_id = request.query_params.get("group_id")
        if not group_id:
            return Response({"error": "group_id param berilmadi"}, status=400)

        group_id = group_id.strip().rstrip("/")

        obj = Interests.objects.filter(group_id=group_id).first()
        if not obj:
            return Response({"error": "Interest mavjud emas"}, status=404)

        ser = InterestsSerializer(obj, context={"request": request})
        return Response(ser.data)

class PublicationByGroupViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PublicationHomeSerializer
    pagination_class = PublicationHome
    def get_queryset(self):
        group_id = self.request.query_params.get("group_id")
        if not group_id:
            raise ValidationError({"group_id": "group_id param berilmadi"})

        group_id = group_id.strip().rstrip("/")

        return (
            Publication.objects
            .filter(group_id=group_id)
            .select_related("publisher", "group")
            .prefetch_related("details", "members")
            .order_by("-created_at")
        )










