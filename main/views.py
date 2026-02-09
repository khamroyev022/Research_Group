from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from  rest_framework import status,viewsets
from .Pagnitions import DefaultPagination
from .models import *
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
    permission_classes=[AllowAny]
    pagination_class = DefaultPagination





























