from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Product_Management.MainStream.Serializers import DownloadsSerializer, ViewDownloadsSerializer, \
    ViewFileDownloadsSerializer
from Product_Management.models import Downloads, FileDownloads
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
    ], responses={200: DownloadsSerializer(many=True)})
    def get(request):
        """This function return the My Library Page Downloads"""
        product_type = request.GET.get("product_type")

        if not product_type:
            return Response({"detail": "product_type is required."}, status=status.HTTP_400_BAD_REQUEST)

        downloads = Downloads.objects.select_related("pack"). \
            prefetch_related("pack__submissions",
                             "pack__submissions__supplier",
                             "pack__submissions__supplier__supplier_details",
                             "pack__submissions__supplier__supplier_details__artist").filter(
            member=request.user,
            pack__submissions__pack_type=product_type,
            pack__submissions__status=SubmissionStatus.APPROVED.value,
        ).only("id", "pack")
        downloads_serializer = ViewDownloadsSerializer(downloads, many=True)
        return Response({'detail': downloads_serializer.data}, status=status.HTTP_200_OK)


class ViewFileDownloadsView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("download_id", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
        openapi.Parameter("pack_id", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True)
    ], responses={200: DownloadsSerializer(many=True)})
    def get(request):
        """This function return the My Library Page Downloads Files"""
        download_id = request.GET.get("download_id")
        pack_id = request.GET.get("pack_id")

        if not download_id:
            return Response({"detail": "download_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not pack_id:
            return Response({"detail": "pack_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        downloads = FileDownloads.objects. \
            select_related("download", "download__pack"). \
            prefetch_related("download__pack__submissions",
                             "download__pack__submissions__supplier",
                             "download__pack__submissions__supplier__supplier_details",
                             "download__pack__submissions__supplier__supplier_details__artist"). \
            filter(download__id=download_id,
                   download__pack__id=pack_id,
                   download__member=request.user,
                   download__pack__submissions__status=SubmissionStatus.APPROVED.value,
                   ). \
            order_by("-created_at")
        downloads_serializer = ViewFileDownloadsSerializer(downloads, many=True)
        return Response({'detail': downloads_serializer.data}, status=status.HTTP_200_OK)


class DownloadsView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(request_body=DownloadsSerializer(),
                         responses={201: "downloads started successfully.", 404: "file not found in pack."})
    def post(request):
        """This function start downloads of a pack or an audio file"""
        downloads_serializer = DownloadsSerializer(data=request.data, context={"user": request.user})
        downloads_serializer.is_valid()
        if downloads_serializer.errors:
            return Response({"detail": extract_error_messages(downloads_serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
        downloads_serializer.save()
        return Response({'detail': "downloads started successfully."}, status=status.HTTP_201_CREATED)
