from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Beats_Management.MainStream.Serializers import BeatsDownloadsSerializer, BeatsViewDownloadsSerializer, \
    BeatsViewFileDownloadsSerializer
from Beats_Management.models import BeatDownloads, BeatFileDownloads
from Utilities import extract_error_messages
from Utilities.Enums import SubmissionStatus
from Utilities.Permissions import MemberPermissions


class ViewDownloadsView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    #
    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("product_type", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
    ], responses={200: BeatsDownloadsSerializer(many=True)})
    def get(request):
        """This function return the My Library Page Downloads"""
        product_type = request.GET.get("product_type")

        if not product_type:
            return Response({"detail": "product_type is required."}, status=status.HTTP_400_BAD_REQUEST)

        downloads = BeatDownloads.objects.select_related("beat"). \
            prefetch_related("beat__submissions",
                             "beat__submissions__supplier",
                             "beat__submissions__supplier__supplier_details",
                             "beat__submissions__supplier__supplier_details__artist").filter(
            member=request.user,
            beat__submissions__beat_type=product_type,
            beat__submissions__status=SubmissionStatus.APPROVED.value,
        ).only("id", "beat")
        downloads_serializer = BeatsViewDownloadsSerializer(downloads, many=True)
        return Response({'detail': downloads_serializer.data}, status=status.HTTP_200_OK)


class ViewFileDownloadsView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("download_id", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
        openapi.Parameter("beat_id", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True)
    ], responses={200: BeatsDownloadsSerializer(many=True)})
    def get(request):
        """This function return the My Library Page Downloads Files"""
        download_id = request.GET.get("download_id")
        beat_id = request.GET.get("beat_id")

        if not download_id:
            return Response({"detail": "download_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not beat_id:
            return Response({"detail": "beat_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        downloads = BeatFileDownloads.objects. \
            select_related("download", "download__beat"). \
            prefetch_related("download__beat__submissions",
                             "download__beat__submissions__supplier",
                             "download__beat__submissions__supplier__supplier_details",
                             "download__beat__submissions__supplier__supplier_details__artist"). \
            filter(download__id=download_id,
                   download__beat__id=beat_id,
                   download__member=request.user,
                   download__beat__submissions__status=SubmissionStatus.APPROVED.value,
                   ). \
            order_by("-created_at")
        downloads_serializer = BeatsViewFileDownloadsSerializer(downloads, many=True)
        return Response({'detail': downloads_serializer.data}, status=status.HTTP_200_OK)


class DownloadsView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(request_body=BeatsDownloadsSerializer(),
                         responses={201: "downloads started successfully.", 404: "file not found in beat."})
    def post(request):
        """This function start downloads of a beat or an audio file"""
        downloads_serializer = BeatsDownloadsSerializer(data=request.data, context={"user": request.user})
        downloads_serializer.is_valid()
        if downloads_serializer.errors:
            return Response({"detail": extract_error_messages(downloads_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        downloads_serializer.save()
        return Response({'detail': "downloads started successfully."}, status=status.HTTP_201_CREATED)
