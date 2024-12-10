from django.db.models import Count
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Product_Management.MainStream.Serializers import PacksSerializer, PackSerializer
from Product_Management.models import PackSubmissions
from Utilities.Enums import PackTypes, SubmissionStatus
from Utilities.Permissions import MemberPermissions


class GetPacksView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("pack_type", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True)
    ], responses={200: PacksSerializer(many=True)})
    def get(request):
        """This function return the Discover Page Packs"""
        pack_type = request.GET.get("pack_type")
        if pack_type in PackTypes.list():
            packs = PackSubmissions.objects.prefetch_related("supplier", "supplier__supplier_details",
                                                             "supplier__supplier_details__artist",
                                                             "pack").filter(pack_type=pack_type,
                                                                            status=SubmissionStatus.APPROVED.value)[:15]
            packs_serializer = PacksSerializer(packs, many=True)
            return Response({'detail': packs_serializer.data}, status=status.HTTP_200_OK)
        return Response({"detail": "invalid pack_type."}, status=status.HTTP_400_BAD_REQUEST)


class ViewPackView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter("id", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
        openapi.Parameter("pack_type", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=True),
    ], responses={200: PackSerializer(many=True)})
    def get(request):
        """This function return the Discover Page Packs Details"""
        id_ = request.GET.get("id")
        pack_type = request.GET.get("pack_type")
        if pack_type in PackTypes.list():
            pack = (PackSubmissions.objects.prefetch_related("supplier", "supplier__supplier_details",
                                                             "supplier__supplier_details__artist",
                                                             "pack", "pack__demo_file", "pack__genre",
                                                             "pack__sub_genre"
                                                             ).filter(pk=id_, pack_type=pack_type,
                                                                      status=SubmissionStatus.APPROVED.value
                                                                      ).annotate(
                files_count=Count('pack__audio_files'))).first()
            if pack:
                pack_serializer = PackSerializer(pack)
                return Response({'detail': pack_serializer.data}, status=status.HTTP_200_OK)
            return Response({"detail": "pack not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid pack_type."}, status=status.HTTP_400_BAD_REQUEST)


class GetSamplesView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: PacksSerializer(many=True)})
    def get(request):
        """This function return the Discover Page Packs"""
        packs = PackSubmissions.objects.prefetch_related("supplier", "supplier__supplier_details",
                                                         "supplier__supplier_details__artist",
                                                         "pack").filter(pack_type=PackTypes.SAMPLE.value,
                                                                        status=SubmissionStatus.APPROVED.value)
        packs_serializer = PacksSerializer(packs, many=True)
        return Response({'detail': packs_serializer.data}, status=status.HTTP_200_OK)


class GetPresetView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: PacksSerializer(many=True)})
    def get(request):
        """This function return the Discover Page Packs"""
        packs = PackSubmissions.objects.prefetch_related("supplier", "supplier__supplier_details",
                                                         "supplier__supplier_details__artist",
                                                         "pack").filter(pack_type=PackTypes.PRESET.value,
                                                                        status=SubmissionStatus.APPROVED.value)
        packs_serializer = PacksSerializer(packs, many=True)
        return Response({'detail': packs_serializer.data}, status=status.HTTP_200_OK)


class GetMIDIView(APIView):
    permission_classes = [IsAuthenticated, MemberPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: PacksSerializer(many=True)})
    def get(request):
        """This function return the Discover Page Packs"""
        packs = PackSubmissions.objects.prefetch_related("supplier", "supplier__supplier_details",
                                                         "supplier__supplier_details__artist",
                                                         "pack").filter(pack_type=PackTypes.MIDI.value,
                                                                        status=SubmissionStatus.APPROVED.value)
        packs_serializer = PacksSerializer(packs, many=True)
        return Response({'detail': packs_serializer.data}, status=status.HTTP_200_OK)
