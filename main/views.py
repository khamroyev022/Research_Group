from rest_framework.response import  Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from dashboard.serializers.Interest_serializer import InterestsSerializer
from dashboard.serializers.serializer import NewsActivitiesSerializer
from .Pagnitions import DefaultPagination,GroupPaginatsion,PublicationHome,NewsPaginatsion
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
                "description": g_tr.description if g_tr else None,
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

    student_obj = ReserchStudent.objects.all()
    if group_id_clean:
        student_obj = student_obj.filter(group_id=group_id_clean)
    student_obj = student_obj.first()

    student_data = None
    if student_obj:
        tg = get_fallback_detail(student_obj.reserchStudent, lang)
        student_data = {
            "id": str(student_obj.id),
            "image": request.build_absolute_uri(student_obj.image.url) if student_obj.image else None,
            "created_at": student_obj.created_at,
            "title": tg.title if tg else None,
        }

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
        "group": group_data,
        "data": {
            "slider": slider_ser.data,
            "achievement": ach_data,
            "partnership": partner_data,
            "research-student": student_data,
            "resources": resours_data,
        }
    }, status=status.HTTP_200_OK)

class NewsViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    pagination_class = PublicationHome

    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        group_id = self.request.query_params.get("group_id")

        qs = (
            NewsActivities.objects
            .select_related("group")
            .prefetch_related("newsactive", "group__details")
            .order_by("-created_at")
        )

        if group_id:
            group_id = group_id.strip().rstrip("/")
            qs = qs.filter(group_id=group_id)

        return qs

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(qs)
        if page is not None:
            ser = NewSerializerHome(page, many=True, context={"request": request})
            return self.get_paginated_response(ser.data)

        ser = NewSerializerHome(qs, many=True, context={"request": request})
        return Response({
            "success": True,
            "message": "OK",
            "data": ser.data,
            "errors": None
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        lang = request.headers.get("Accept-Language", "uz")

        detail = (
            NewsActivitiesDetail.objects
            .filter(slug=slug, language=lang)
            .select_related("newsdetail")
            .first()
        )

        if not detail and lang != "uz":
            detail = (
                NewsActivitiesDetail.objects
                .filter(slug=slug, language="uz")
                .select_related("newsdetail")
                .first()
            )

        if not detail:
            return Response({
                "success": False,
                "message": "Topilmadi",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        news = detail.newsdetail
        ser = NewsSerializer(news, context={"request": request})

        return Response({
            "success": True,
            "message": "OK",
            "data": ser.data,
            "errors": None
        }, status=status.HTTP_200_OK)

class ConferencesViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    pagination_class = PublicationHome

    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        group_id = self.request.query_params.get("group_id")

        qs = (
            ConferencesSeminars.objects
            .select_related("group")
            .prefetch_related("conferencesseminars", "group__details")
            .order_by("-created_at")
        )

        if group_id:
            group_id = group_id.strip().rstrip("/")
            qs = qs.filter(group_id=group_id)

        return qs

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(qs)
        if page is not None:
            ser = ConferensiaHomeSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(ser.data)

        ser = ConferensiaHomeSerializer(qs, many=True, context={"request": request})
        return Response({
            "success": True,
            "message": "OK",
            "data": ser.data,
            "errors": None
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        lang = request.headers.get("Accept-Language", "uz")

        detail = (
            ConferencesSeminarsDetail.objects
            .filter(slug=slug, language=lang)
            .select_related("conferencesseminars")
            .first()
        )

        if not detail and lang != "uz":
            detail = (
                ConferencesSeminarsDetail.objects
                .filter(slug=slug, language="uz")
                .select_related("conferencesseminars")
                .first()
            )

        if not detail:
            return Response({
                "success": False,
                "message": "Topilmadi",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        obj = detail.conferencesseminars
        ser = ConferensiaHomeSerializer(obj, context={"request": request})

        return Response({
            "success": True,
            "message": "OK",
            "data": ser.data,
            "errors": None
        }, status=status.HTTP_200_OK)

class MemberByGroupView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        group_id = request.query_params.get("group_id")
        if not group_id:
            return Response({"error": "group_id param berilmadi"}, status=400)

        group_id = group_id.strip().rstrip("/")

        qs = (
            Member.objects
            .filter(group_id=group_id, status="completed")
            .select_related("group", "country", "university")
            .prefetch_related("details", "group__details", "country__details", "university__details")
        )

        serializer = MemberGetSerializer(qs, many=True, context={"request": request})
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

class ProjectsViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ProjectsSerializer
    pagination_class = GroupPaginatsion

    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        request = self.request
        group_id = request.query_params.get("group_id")
        status_param = request.query_params.get("status")

        qs = (
            Projects.objects
            .select_related("group", "sponsor_university", "sponsor_country")
            .prefetch_related(
                "translations",
                "group__details",
                "sponsor_university__details",
                "sponsor_country__details"
            )
            .order_by("-start_date")
        )

        if group_id:
            group_id = group_id.strip().rstrip("/")
            qs = qs.filter(group_id=group_id)

        if status_param is not None:
            s = status_param.lower()
            if s in ("true", "1", "yes"):
                qs = qs.filter(status=True)
            elif s in ("false", "0", "no"):
                qs = qs.filter(status=False)

        return qs

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        lang = request.headers.get("Accept-Language", "uz")

        detail = (
            ProjectsTranslate.objects
            .filter(slug=slug, language=lang)
            .select_related("projects")
            .first()
        )

        if not detail and lang != "uz":
            detail = (
                ProjectsTranslate.objects
                .filter(slug=slug, language="uz")
                .select_related("projects")
                .first()
            )

        if not detail:
            return Response({
                "success": False,
                "message": "Topilmadi",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        obj = detail.projects
        ser = self.get_serializer(obj, context={"request": request})

        return Response({
            "success": True,
            "message": "OK",
            "data": ser.data,
            "errors": None
        })

class MediaViews(APIView):
    pagination_class = PublicationHome
    permission_classes = [AllowAny]
    def get(self, request):
        group_id = request.query_params.get("group_id")

        if not group_id:
            return Response({"error": "group_id param berilmadi"}, status=404)
        group_id = group_id.strip().rstrip("/")

        qs = GroupMedia.objects.filter(group_id=group_id)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request, view=self)

        ser= MediaSerializer(qs, many=True, context={"request": request})
        return paginator.get_paginated_response(ser.data)

class SocialLinkViewSet(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        group_id = request.query_params.get("group_id")

        if not group_id:
            return Response({"error": "group_id param berilmadi"}, status=400)
        group_id = group_id.strip().rstrip("/")
        qs = SosialLink.objects.filter(group_id=group_id)

        ser = SociallinkSerializer(qs, many=True, context={"request": request})
        return Response(ser.data)

class PublicationViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    pagination_class = PublicationHome

    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        group_id = self.request.query_params.get("group_id")

        qs = (
            Publication.objects
            .select_related("publisher", "group")
            .prefetch_related(
                "details",
                "members",
                "members__details",
                "group__details",
            )
            .order_by("-created_at")
        )

        if group_id:
            group_id = group_id.strip().rstrip("/")
            qs = qs.filter(group_id=group_id)

        return qs

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(qs)
        if page is not None:
            ser = PublicationHomeSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(ser.data)

        ser = PublicationHomeSerializer(qs, many=True, context={"request": request})
        return Response({
            "success": True,
            "message": "OK",
            "data": ser.data,
            "errors": None
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        lang = request.headers.get("Accept-Language", "uz")

        detail = (
            PublicationDetail.objects
            .filter(slug=slug, language=lang)
            .select_related("publication")
            .first()
        )

        if not detail and lang != "uz":
            detail = (
                PublicationDetail.objects
                .filter(slug=slug, language="uz")
                .select_related("publication")
                .first()
            )

        if not detail:
            return Response({
                "success": False,
                "message": "Topilmadi",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        pub = detail.publication
        ser = PublicationDetailSerializer(pub, context={"request": request})

        return Response({
            "success": True,
            "message": "OK",
            "data": ser.data,
            "errors": None
        }, status=status.HTTP_200_OK)














































