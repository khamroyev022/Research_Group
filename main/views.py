from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from  rest_framework import status,viewsets
from .models import *
from .serializer import *
from rest_framework import status


@api_view(["GET"])
@permission_classes([AllowAny])
def group_list_api(request):
    lang = request.headers.get("Accept-Language", "uz")
    qs = Group.objects.all().prefetch_related("group")

    serializer = GroupSerializer(qs, many=True, context={"language": lang, "request": request})
    return Response({
        "language": lang,
        "data":serializer.data
    },status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([AllowAny])
def direction_list_list(request):
    lang = request.headers.get("Accept-Language", "uz")
    qs = Direction.objects.all().prefetch_related("details")

    ser = DirectionSerializer(qs, many=True, context={"language": lang})
    return Response({
        "language": lang,
        "data":ser.data
    },status=status.HTTP_200_OK)












































