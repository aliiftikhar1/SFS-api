from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Product_Management.Serializers import MoodSerializer, MoodsDropdownSerializer
from Product_Management.models import Mood
from Utilities import extract_error_messages
from Utilities.Permissions import AdminPermissions, SupplierPermissions


class MoodsDropdownView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions | SupplierPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: MoodsDropdownSerializer(many=True)})
    def get(request):
        """This function return the moodsDropdown list."""
        moods = Mood.objects.all()
        moods_serializer = MoodsDropdownSerializer(moods, many=True)
        return Response({'detail': moods_serializer.data}, status=status.HTTP_200_OK)


class MoodsView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: MoodSerializer(many=True)})
    def get(request):
        """This function return the mood."""
        mood = Mood.objects.all()
        mood_serializer = MoodSerializer(mood, many=True)
        return Response({'detail': mood_serializer.data}, status=status.HTTP_200_OK)

    @staticmethod
    @swagger_auto_schema(request_body=MoodSerializer(),
                         responses={200: "mood created successfully"})
    def post(request):
        """This function create the mood based on given data"""
        mood_serializer = MoodSerializer(data=request.data)
        mood_serializer.is_valid()
        if mood_serializer.errors:
            return Response({"detail": extract_error_messages(mood_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        mood_serializer.save()
        return Response({"detail": "mood created successfully"}, status=status.HTTP_201_CREATED)

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("mood_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("mood_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "mood deleted successfully", 404: "mood not found!"})
    def delete(request):
        """This function deletes the mood based on given data"""
        mood_id = request.GET.get("mood_id")
        mood_name = request.GET.get("mood_name")
        mood = Mood.objects.filter(pk=mood_id, name=mood_name).first()
        if mood:
            try:
                mood.delete()
                return Response({"detail": "mood deleted successfully"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "mood not found"}, status=status.HTTP_404_NOT_FOUND)
