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

    serializer = GroupOneLangSerializer(qs, many=True, context={"language": lang})
    return Response({
        "language": lang,
        "data":serializer.data
    },status=status.HTTP_200_OK)