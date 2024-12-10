from django.db.models import Count
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Beats_Management.MainStream.Serializers import BeatsSerializer, BeatSerializer
from Beats_Management.models import BeatsSubmissions
from Utilities.Enums import BeatTypes, SubmissionStatus
from Utilities.Permissions import MemberPermissions, AdminPermissions 


class GetBeatsView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("beat_type", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True)
    ], responses={200: BeatsSerializer(many=True)})
    def get(request):
        """This function return the Discover Page Beats"""
        beat_type = request.GET.get("beat_type")
        if beat_type in BeatTypes.list():
            beats = BeatsSubmissions.objects.prefetch_related("supplier", "supplier__supplier_details",
                                                             "supplier__supplier_details__artist",
                                                             "beat").filter(beat_type=beat_type,
                                                                            status=SubmissionStatus.APPROVED.value)[:15]
            beats_serializer = BeatsSerializer(beats, many=True)
            return Response({'detail': beats_serializer.data}, status=status.HTTP_200_OK)
        return Response({"detail": "invalid beat_type."}, status=status.HTTP_400_BAD_REQUEST)


class ViewBeatView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("id", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
        openapi.Parameter("beat_type", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
    ], responses={200: BeatSerializer(many=True)})
    def get(request):
        """This function return the Discover Page Beats Details"""
        id_ = request.GET.get("id")
        beat_type = request.GET.get("beat_type")
        if beat_type in BeatTypes.list():
            beat = (BeatsSubmissions.objects.prefetch_related("supplier", "supplier__supplier_details",
                                                             "supplier__supplier_details__artist",
                                                             "beat", "beat__demo_file", "beat__genre",
                                                             "beat__sub_genre"
                                                             ).filter(pk=id_, beat_type=beat_type,
                                                                      status=SubmissionStatus.APPROVED.value
                                                                      ).annotate(
                files_count=Count('beat__audio_files'))).first()
            if beat:
                beat_serializer = BeatSerializer(beat)
                return Response({'detail': beat_serializer.data}, status=status.HTTP_200_OK)
            return Response({"detail": "beat not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid beat_type."}, status=status.HTTP_400_BAD_REQUEST)


class GetAllBeatsView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions | AdminPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: BeatsSerializer(many=True)})
    def get(request):
        """This function return the Discover Page Beats"""
        beats = BeatsSubmissions.objects.prefetch_related("supplier", "supplier__supplier_details",
                                                         "supplier__supplier_details__artist",
                                                         "beat").filter(beat_type=BeatTypes.BEAT.value,
                                                                        status=SubmissionStatus.APPROVED.value)
        beats_serializer = BeatsSerializer(beats, many=True)
        return Response({'detail': beats_serializer.data}, status=status.HTTP_200_OK)


# class GetPresetView(APIView):
#     permission_classes = [IsAuthenticated, MemberPermissions]

#     @staticmethod
#     @swagger_auto_schema(responses={200: BeatsSerializer(many=True)})
#     def get(request):
#         """This function return the Discover Page Beats"""
#         beats = BeatsSubmissions.objects.prefetch_related("supplier", "supplier__supplier_details",
#                                                          "supplier__supplier_details__artist",
#                                                          "beat").filter(beat_type=BeatTypes.zip.value,
#                                                                         status=SubmissionStatus.APPROVED.value)
#         beats_serializer = BeatsSerializer(beats, many=True)
#         return Response({'detail': beats_serializer.data}, status=status.HTTP_200_OK)


# class GetMIDIView(APIView):
#     permission_classes = [IsAuthenticated, MemberPermissions]

#     @staticmethod
#     @swagger_auto_schema(responses={200: BeatsSerializer(many=True)})
#     def get(request):
#         """This function return the Discover Page Beats"""
#         beats = BeatsSubmissions.objects.prefetch_related("supplier", "supplier__supplier_details",
#                                                          "supplier__supplier_details__artist",
#                                                          "beat").filter(beat_type=BeatTypes.wav.value,
#                                                                         status=SubmissionStatus.APPROVED.value)
#         beats_serializer = BeatsSerializer(beats, many=True)
#         return Response({'detail': beats_serializer.data}, status=status.HTTP_200_OK)
