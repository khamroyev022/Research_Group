import uuid
from rest_framework.decorators import api_view,APIView,permission_classes,action
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from main.models import *
from .models import CustomerUser
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
from .filters import *

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
        }
    }, status=status.HTTP_200_OK)

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
    # permission_classes = [IsAuthenticated]
    pagination_class = None
    permission_classes=[AllowAny]
    search_fields =['name']
    def get_serializer_context(self):
            context = super().get_serializer_context()
            context['language'] = self.request.headers.get('Accept-Language', 'uz')
            return context

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
    search_fields =['name','description']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')  
        return context

class GroupViewset(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['is_active', 'direction']
    search_fields = ['group__name', 'group__description']
    ordering_fields = ['id', 'created']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context


class UniversityViews(ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
    def get_serializer_context(self):
        contex = super().get_serializer_context()
        contex['language'] = self.request.headers.get('Accept-Language', 'uz')
        return contex

@api_view(["PATCH", "GET"])
@permission_classes([AllowAny])
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
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = MemberFilter  # <-- mana shu

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class PublicationViewSet(ModelViewSet):
    queryset = Publication.objects.all().order_by('created_at')
    serializer_class = PublicationSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['group','publisher',]
    search_fields  = ['title']


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class PublishViewset(ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class ProjectsViewSet(ModelViewSet):
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class InterestsViewSet(ModelViewSet):
    queryset = Interests.objects.all()
    serializer_class = InterestsSerializer
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
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
                return Response({"detail": "Topilmadi"}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)


        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PartnershipViewSet(ModelViewSet):
    queryset = Partnership.objects.all()
    serializer_class = PartnershipSerializer
    permission_classes = [AllowAny]
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
        qs = self.filter_queryset(self.get_queryset())

        if qs.count()==1:
            obj = qs.first()
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if qs.count()== 0:
            return Response({"error": "Topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(qs,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ReserchStudentViewSet(ModelViewSet):
    queryset = ReserchStudent.objects.all()
    serializer_class = ReserchStudentSerializer
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
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
        qs = self.filter_queryset(self.get_queryset())


        if qs.count() == 1:
            obj = qs.first()
            serializer = self.get_serializer(obj)
            return Response(serializer.data)

        if qs.count() == 0:
            return Response({"detail": "Topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class NewsActivitiesViewSet(ModelViewSet):
    queryset = NewsActivities.objects.all()
    serializer_class = NewsActivitiesSerializer
    permission_classes = [AllowAny]
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


class ConferencesSeminarsViewSet(ModelViewSet):
    queryset = ConferencesSeminars.objects.all()
    serializer_class = ConferencesSeminarsSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = DefaultPagination

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
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
    pagination_class = None
    def get_queryset(self):
        qs = super().get_queryset()
        group_id = self.request.query_params.get('group_id')

        if group_id:
            qs = qs.filter(group_id=group_id)

        return qs















