import uuid
from rest_framework.decorators import api_view,APIView,permission_classes,action
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from main.models import *
from .models import CustomerUser, PasswordResetCode
from .serializers.direction_serializer import *
from .serializers.group_serializer import *
from .serializers.login_serialzer import *
from .serializers.Interest_serializer import *
from .serializers.serializer import *
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from .pagination import DefaultPagination
from .serializers.projects_serializer import *
from rest_framework.decorators import parser_classes
from django_filters.rest_framework import DjangoFilterBackend
from .serializers.Restartpasswordserializer import *
from .filters import *

import random
from django.core.mail import send_mail

@api_view(["POST"])
@permission_classes([AllowAny])
def loginviews(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'username va password majburiy'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = CustomerUser.objects.filter(username=username).first()

    if user is None:
        return Response(
            {'error': 'foydalanuvchi mavjud emas'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not user.check_password(password):
        return Response(
            {'error': 'parol xato'},
            status=status.HTTP_400_BAD_REQUEST
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'username': user.username,
            "Admin":"Adminstrator",
            "email": user.email,
        }
    }, status=status.HTTP_200_OK)

def generate_code():
    return f"{random.randint(0, 999999):06d}"


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    ser = ForgotPasswordSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    email = ser.validated_data["email"]
    user = CustomerUser.objects.filter(email=email).first()
    if not user:
        return Response({"error": "Bunday email topilmadi"}, status=status.HTTP_404_NOT_FOUND)

    code = generate_code()

    PasswordResetCode.objects.filter(user=user, is_used=False).update(is_used=True)

    PasswordResetCode.objects.create(user=user, code=code)

    send_mail(
        subject="Parolni tiklash kodi",
        message=f"Sizning parolni tiklash kodingiz: {code}\nKod 10 daqiqa amal qiladi.",
        from_email=None,
        recipient_list=[email],
        fail_silently=False
    )

    return Response({"success": "Kod emailga yuborildi"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_reset_code(request):
    ser = VerifyResetCodeSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    email = ser.validated_data["email"]
    code = ser.validated_data["code"]

    user = CustomerUser.objects.filter(email=email).first()
    if not user:
        return Response({"error": "Bunday email topilmadi"}, status=status.HTTP_404_NOT_FOUND)

    obj = PasswordResetCode.objects.filter(user=user, code=code, is_used=False).order_by("-created_at").first()
    if not obj:
        return Response({"error": "Kod noto‘g‘ri"}, status=status.HTTP_400_BAD_REQUEST)

    if obj.is_expired():
        return Response({"error": "Kod muddati tugagan"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"success": "Kod to‘g‘ri"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    ser = ResetPasswordSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    email = ser.validated_data["email"]
    code = ser.validated_data["code"]
    new_password = ser.validated_data["new_password"]

    user = CustomerUser.objects.filter(email=email).first()
    if not user:
        return Response({"error": "Bunday email topilmadi"}, status=status.HTTP_404_NOT_FOUND)

    obj = PasswordResetCode.objects.filter(user=user, code=code, is_used=False).order_by("-created_at").first()
    if not obj:
        return Response({"error": "Kod noto‘g‘ri"}, status=status.HTTP_400_BAD_REQUEST)

    if obj.is_expired():
        return Response({"error": "Kod muddati tugagan"}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    obj.is_used = True
    obj.save()

    return Response({"success": "Parol yangilandi"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    ser = RegSerializer(data=request.data)
    if ser.is_valid():
        user = ser.save()
        return Response({
                'success': 'foydalanuvchi yaratildi',
                'user_id': user.id,
                'username': user.username
            },status=status.HTTP_201_CREATED)
    return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)

class DirectionCRUDViews(ModelViewSet):
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    search_fields =['name']
    def get_serializer_context(self):
            context = super().get_serializer_context()
            context['language'] = self.request.headers.get('Accept-Language', 'uz')
            return context

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    search_fields =['name','description']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')  
        return context

class GroupViewset(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['is_active', 'direction']
    search_fields = ['details__name', 'details__description']
    ordering_fields = ['id', 'created']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class UniversityViews(ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    def get_serializer_context(self):
        contex = super().get_serializer_context()
        contex['language'] = self.request.headers.get('Accept-Language', 'uz')
        return contex

@api_view(["PATCH", "GET"])
@permission_classes([IsAuthenticated])
def groupactiveviews(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response(
            {"error": "bunday group id mavjud emas"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        return Response({
            "is_active": group.is_active
        }, status=status.HTTP_200_OK)

    if request.method == "PATCH":
        group.is_active = not group.is_active
        group.save()

        return Response({
            "is_active": group.is_active
        }, status=status.HTTP_200_OK)

class MemberViewset(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MemberFilter
    search_fields = [
        'details__full_name',
        'email',
        'phone',
        'details__affiliation',
    ]

    ordering_fields = ['created', 'status', 'email']
    ordering = ['-created']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class PublicationViewSet(ModelViewSet):
    queryset = Publication.objects.all().order_by('created_at')
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PublicationFilter
    search_fields = ['details__title', 'details__topic']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class PublishViewset(ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class ProjectsViewSet(ModelViewSet):
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProjectsFilter
    search_fields = [
        'translations__title',
        'translations__topic',
        'translations__description',
    ]
    ordering_fields = ['amount', 'start_date', 'end_date', 'id']
    ordering = ['-id']
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class InterestsViewSet(ModelViewSet):
    queryset = Interests.objects.all()
    serializer_class = InterestsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        group_id = self.request.query_params.get('group_id')
        if group_id:
            return queryset.filter(group_id=group_id)
        return queryset

    def list(self, request, *args, **kwargs):
        group_id = request.query_params.get('group_id')
        if group_id:
            interests = self.get_queryset().first()
            if not interests:
                return Response(
                    {"error": "bunday group id uchun interests topilmadi"},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(interests)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='by-group/(?P<group_id>[^/.]+)')
    def by_group(self, request, group_id=None):
        interests = Interests.objects.filter(group_id=group_id).first()
        if not interests:
            return Response(
                {"error": "bunday group id uchun interests topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(interests)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AchivmentViewSet(ModelViewSet):
    queryset = Achivment.objects.all()
    serializer_class = AchivmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = super().get_queryset()
        group_id = self.request.query_params.get("group_id")
        if group_id:
            return queryset.filter(group_id=group_id.rstrip("/"))
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

    def list(self, request, *args, **kwargs):
        group_id = request.query_params.get("group_id")
        qs = self.filter_queryset(self.get_queryset())

        if group_id:
            obj = qs.order_by("-created_at").first()
            if not obj:
                return Response(
                    {"group_id": group_id, "achivment": None},
                    status=status.HTTP_200_OK
                )

            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PartnershipViewSet(ModelViewSet):
    queryset = Partnership.objects.all()
    serializer_class = PartnershipSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        group_id = self.request.query_params.get("group_id")
        if group_id:
            group_id = group_id.strip().rstrip("/")
            qs = qs.filter(group_id=group_id)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # request DRF contextda bor bo'ladi, lekin qoldiramiz
        context["request"] = self.request
        context["language"] = self.request.headers.get("Accept-Language", "uz")
        return context

    def list(self, request, *args, **kwargs):
        group_id = request.query_params.get("group_id")
        qs = self.filter_queryset(self.get_queryset())

        if group_id:
            obj = qs.first()
            if not obj:
                return Response(
                    {"group_id": group_id, "partnership": None},
                    status=status.HTTP_200_OK
                )
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReserchStudentViewSet(ModelViewSet):
    queryset = ReserchStudent.objects.all()
    serializer_class = ReserchStudentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = super().get_queryset()
        group_id = self.request.query_params.get("group_id")
        if group_id:
            return queryset.filter(group_id=group_id.rstrip("/"))
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class ResourcesViewSet(ModelViewSet):
    queryset = Resources.objects.all()
    serializer_class = ResourcesSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = super().get_queryset()
        group_id = self.request.query_params.get("group_id")
        if group_id:
            group_id = group_id.strip().rstrip("/")
            qs = qs.filter(group_id=group_id)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        context["language"] = self.request.headers.get("Accept-Language", "uz")
        return context

    def list(self, request, *args, **kwargs):
        group_id = request.query_params.get("group_id")
        qs = self.filter_queryset(self.get_queryset())

        if group_id:
            obj = qs.first()
            if not obj:
                return Response(
                    {"group_id": group_id, "resources": None},
                    status=status.HTTP_200_OK
                )
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # group_id bo'lmasa — list
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NewsActivitiesViewSet(ModelViewSet):
    queryset = NewsActivities.objects.all()
    serializer_class = NewsActivitiesSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    parser_classes = [MultiPartParser, FormParser]
    filterset_class = NewsActivitiesFilter
    filter_backends = [DjangoFilterBackend,SearchFilter        ]
    search_fields = [
        'newsactive__title',
        'newsactive__description',
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        group_id = self.request.query_params.get("group_id")
        if group_id:
            return queryset.filter(group_id=group_id.rstrip("/"))
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class ConferencesSeminarsViewSet(ModelViewSet):
    queryset = ConferencesSeminars.objects.all()
    serializer_class = ConferencesSeminarsSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = DefaultPagination
    django_filters = [DjangoFilterBackend,SearchFilter]
    search_fields = [
        "conferencesseminars__title",
        "conferencesseminars__description",
    ]
    def get_queryset(self):
        queryset = super().get_queryset()
        group_id = self.request.query_params.get("group_id")
        if group_id:
            return queryset.filter(group_id=group_id.rstrip("/"))
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class SliderGroupViewSet(ModelViewSet):
    queryset = SliderGroup.objects.all()
    serializer_class = SliderGroupSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = super().get_queryset()
        group_id = self.request.query_params.get("group_id")
        if group_id:
            return queryset.filter(group_id=group_id.rstrip("/"))
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class GroupMediaViewSet(ModelViewSet):
    queryset = GroupMedia.objects.select_related("group").all().order_by("-id")
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = GroupMedia.objects.select_related("group").all().order_by("-id")
        group_id = self.request.query_params.get("group_id")
        if not group_id:
            return queryset
        group_id = group_id.rstrip("/")
        try:
            uuid.UUID(group_id)
        except (ValueError, AttributeError):
            return queryset.none()
        return queryset.filter(group_id=group_id)

    def list(self, request, *args, **kwargs):
        group_id = request.query_params.get("group_id")
        if group_id:
            group_id = group_id.rstrip("/")
            try:
                uuid.UUID(group_id)
            except (ValueError, AttributeError):
                return Response(
                    {"error": "group_id UUID formatida bo‘lishi kerak"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        group_id = request.data.get("group_id")
        if not group_id:
            return Response(
                {"error": "group_id maydoni majburiy"},
                status=status.HTTP_400_BAD_REQUEST
            )

        group = Group.objects.filter(id=group_id).first()
        if not group:
            return Response(
                {"error": "Bunday guruh mavjud emas"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        media = serializer.save(group=group)

        out = self.get_serializer(media)
        return Response(out.data, status=status.HTTP_201_CREATED)

class SosialLinkViewset(ModelViewSet):
    queryset = SosialLink.objects.all()
    serializer_class = SocialLinkSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    def get_queryset(self):
        qs = super().get_queryset()
        group_id = self.request.query_params.get('group_id')

        if group_id:
            qs = qs.filter(group_id=group_id)

        return qs



@api_view(['GET'])
@permission_classes([AllowAny])
def statictika(request):
    group_count = Group.objects.count()
    member_count = Member.objects.count()
    country_count = Country.objects.count()
    publication_count = Publication.objects.count()
    news_count = News.objects.count()
    confiresnising_count = ConferencesSeminars.objects.count()
    return Response({
        "group_count": group_count,
        "member_count": member_count,
        "country_count": country_count,
        "publication_count": publication_count,
        "news_count": news_count,
        "confiresnising_count": confiresnising_count
    },status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def email_update(request,pk):
    try :
        user = CustomerUser.objects.get(pk=pk)
    except CustomerUser.DoesNotExist:
        return Response({
            "error": "User not found"
        },status=status.HTTP_404_NOT_FOUND)
    ser = RegSerializer(user, data=request.data, partial=True)
    if ser.is_valid(raise_exception=True):
        ser.save()
        return Response(ser.data)
























