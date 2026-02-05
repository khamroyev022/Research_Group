from django.test import TestCase

# Create your tests here.
from rest_framework.decorators import api_view,APIView,permission_classes,action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
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
from .serializers.news_serializer import *
from .pagination import DefaultPagination
from .serializers.projects_serializer import *
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
    def get_serializer_context(self):
            context = super().get_serializer_context()
            context['language'] = self.request.headers.get('Accept-Language', 'uz')
            return context

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.headers.get('Accept-Language', 'uz')
        return context

class NewsListAPIView(ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class PublicationViewSet(ModelViewSet):
    queryset = Publication.objects.all().order_by('created_at')
    serializer_class = PublicationSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
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
























