from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Product_Management.Serializers import PackSubmissionsSerializer, ViewPacksSerializer, RevisedAudioFileSerializer
from Product_Management.models import PackSubmissions
from Utilities.Enums import PackTypes, SubmissionStatus, FileStatus, Boolean
from Utilities.Permissions import AdminPermissions, StaffPermissions, SupplierPermissions


class PackSubmissionsView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions | SupplierPermissions]

    @staticmethod
    @swagger_auto_schema(request_body=PackSubmissionsSerializer(),
                         responses={200: "pack submitted successfully"})
    def post(request):
        """This function handles pack-submissions"""
        try:
            with transaction.atomic():
                packs_submissions_serializer = PackSubmissionsSerializer(data=request.data,
                                                                         context={"supplier": request.user})
                packs_submissions_serializer.is_valid()

                if packs_submissions_serializer.errors:
                    return Response({"detail": packs_submissions_serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

                packs_submissions_serializer.save()
                return Response({"detail": "pack submitted successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ViewPacksView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions | StaffPermissions | SupplierPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("pack_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING),
            openapi.Parameter("pack_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING)
        ],
        responses={200: ViewPacksSerializer(many=True), 404: "pack not found!"})
    def get(request):
        """This function handles pack-submissions"""
        pack_id = request.GET.get("pack_id")
        pack_type = request.GET.get("pack_type")
        if pack_type in PackTypes.list():
            queryset = {}
            if pack_id:
                queryset["pk"] = pack_id
            if pack_type:
                queryset['pack_type'] = pack_type
            if request.user.is_supplier or request.user.is_admin:
                queryset['supplier'] = request.user
            pack = PackSubmissions.objects.select_related("pack", "supplier").filter(**queryset)
            view_packs_serializer = ViewPacksSerializer(pack, many=True)
            return Response({"detail": view_packs_serializer.data}, status=status.HTTP_200_OK)
        return Response({"detail": "invalid pack type"}, status=status.HTTP_404_NOT_FOUND)


class SendRevisionPacksView(APIView):
    permission_classes = [IsAuthenticated, StaffPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("pack_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("supplier_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("file_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("file_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("file_revision_message", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("is_demo_file", in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=True)
        ],
        responses={200: ViewPacksSerializer(many=True), 400: "cannot send revision", 404: "pack not found!"})
    def patch(request):
        """This function handles pack-revisions"""
        request_id = request.GET.get("request_id")
        pack_id = request.GET.get("pack_id")
        pack_title = request.GET.get("pack_title")
        pack_type = request.GET.get("pack_type")
        supplier_id = request.GET.get("supplier_id")
        file_id = request.GET.get("file_id")
        file_name = request.GET.get("file_name")
        file_revision_message = request.GET.get("file_revision_message")
        is_demo_file = request.GET.get("is_demo_file")

        if pack_type in PackTypes.list():
            submission = PackSubmissions.objects.select_related("pack", "pack__demo_file", "supplier").filter(
                id=request_id, pack__id=pack_id,
                pack__title=pack_title,
                supplier__id=supplier_id,
                pack_type=pack_type).first()
            if submission:
                if not (submission.status in [SubmissionStatus.UPLOADED, SubmissionStatus.PROCESS]):
                    return Response({"detail": "cannot send revisions!"}, status=status.HTTP_400_BAD_REQUEST)
                if Boolean.get_bool(is_demo_file):
                    if str(submission.pack.demo_file.file.id) != file_id or \
                            submission.pack.demo_file.file.file_name != file_name:
                        return Response({"detail": "file not found!"}, status=status.HTTP_404_NOT_FOUND)
                    file = submission.pack.demo_file
                else:
                    audio_file = submission.pack.audio_files.select_related("file"). \
                        filter(file__id=file_id, file__file_name=file_name).first()
                    if not audio_file:
                        return Response({"detail": "file not found!"}, status=status.HTTP_404_NOT_FOUND)
                    file = audio_file
                file.message = file_revision_message
                file.status = FileStatus.REVISE
                file.save(update_fields=["message", "status"])
                file.status = SubmissionStatus.PROCESS
                file.save(update_fields=["status"])
                return Response({"detail": "file revision added successfully!"}, status=status.HTTP_200_OK)
            return Response({"detail": "pack not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid pack type"}, status=status.HTTP_400_BAD_REQUEST)


class ResolveRevisionPacksView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions | SupplierPermissions]

    @staticmethod
    @swagger_auto_schema(
        request_body=RevisedAudioFileSerializer(),
        responses={200: "pack revised successfully", 404: "pack submission does not exist!"})
    def post(request):
        """This function resolve pack-revisions"""
        try:
            with transaction.atomic():
                packs_revision_serializer = RevisedAudioFileSerializer(data=request.data,
                                                                       context={"user": request.user})
                packs_revision_serializer.is_valid()

                if packs_revision_serializer.errors:
                    return Response({"detail": packs_revision_serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

                packs_revision_serializer.save()
                return Response({"detail": "pack revised successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ApproveRevisionPacksView(APIView):
    permission_classes = [IsAuthenticated, StaffPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("pack_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("supplier_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("file_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("file_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("is_demo_file", in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=True)
        ],
        responses={200: "file approved successfully!", 400: "cannot approve file", 404: "pack not found!"})
    def patch(request):
        """This function handles pack-approval"""
        request_id = request.GET.get("request_id")
        pack_id = request.GET.get("pack_id")
        pack_title = request.GET.get("pack_title")
        pack_type = request.GET.get("pack_type")
        supplier_id = request.GET.get("supplier_id")
        file_id = request.GET.get("file_id")
        file_name = request.GET.get("file_name")
        is_demo_file = request.GET.get("is_demo_file")

        if pack_type in PackTypes.list():
            submission = PackSubmissions.objects.select_related("pack", "pack__demo_file", "supplier").filter(
                id=request_id, pack__id=pack_id,
                pack__title=pack_title,
                supplier__id=supplier_id,
                pack_type=pack_type).first()
            if submission:
                if not (submission.status in [SubmissionStatus.UPLOADED, SubmissionStatus.PROCESS]):
                    return Response({"detail": "cannot approve file!"}, status=status.HTTP_400_BAD_REQUEST)

                if Boolean.get_bool(is_demo_file):
                    if str(submission.pack.demo_file.file.id) != file_id or \
                            submission.pack.demo_file.file.file_name != file_name:
                        return Response({"detail": "file not found!"}, status=status.HTTP_404_NOT_FOUND)
                    file = submission.pack.demo_file
                else:
                    audio_file = submission.pack.audio_files.select_related("file"). \
                        filter(file__id=file_id, file__file_name=file_name).first()
                    if not audio_file:
                        return Response({"detail": "file not found!"}, status=status.HTTP_404_NOT_FOUND)
                    file = audio_file

                if not (file.status in [FileStatus.UPLOADED, FileStatus.REVISED]):
                    return Response({"detail": "cannot approve file!"}, status=status.HTTP_400_BAD_REQUEST)

                file.status = FileStatus.APPROVED
                file.save(update_fields=["status"])
                file.status = SubmissionStatus.PROCESS
                file.save(update_fields=["status"])
                return Response({"detail": "file approved successfully!"}, status=status.HTTP_200_OK)
            return Response({"detail": "pack not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid pack type"}, status=status.HTTP_400_BAD_REQUEST)


class RejectRevisionPacksView(APIView):
    permission_classes = [IsAuthenticated, StaffPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("pack_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("supplier_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("file_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("file_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("is_demo_file", in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=True)
        ],
        responses={200: "file rejected successfully!", 400: "cannot approve file", 404: "pack not found!"})
    def patch(request):
        """This function handles pack-rejection"""
        request_id = request.GET.get("request_id")
        pack_id = request.GET.get("pack_id")
        pack_title = request.GET.get("pack_title")
        pack_type = request.GET.get("pack_type")
        supplier_id = request.GET.get("supplier_id")
        file_id = request.GET.get("file_id")
        file_name = request.GET.get("file_name")
        is_demo_file = request.GET.get("is_demo_file")

        if pack_type in PackTypes.list():
            submission = PackSubmissions.objects.select_related("pack", "pack__demo_file", "supplier").filter(
                id=request_id, pack__id=pack_id,
                pack__title=pack_title,
                supplier__id=supplier_id,
                pack_type=pack_type).first()
            if submission:
                if not (submission.status in [SubmissionStatus.UPLOADED, SubmissionStatus.PROCESS]):
                    return Response({"detail": "cannot approve file!"}, status=status.HTTP_400_BAD_REQUEST)

                if Boolean.get_bool(is_demo_file):
                    if str(submission.pack.demo_file.file.id) != file_id or \
                            submission.pack.demo_file.file.file_name != file_name:
                        return Response({"detail": "file not found!"}, status=status.HTTP_404_NOT_FOUND)
                    file = submission.pack.demo_file
                else:
                    audio_file = submission.pack.audio_files.select_related("file"). \
                        filter(file__id=file_id, file__file_name=file_name).first()
                    if not audio_file:
                        return Response({"detail": "file not found!"}, status=status.HTTP_404_NOT_FOUND)
                    file = audio_file

                file.status = FileStatus.REJECTED
                file.save(update_fields=["status"])
                file.status = SubmissionStatus.PROCESS
                file.save(update_fields=["status"])
                return Response({"detail": "file rejected successfully!"}, status=status.HTTP_200_OK)
            return Response({"detail": "pack not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid pack type"}, status=status.HTTP_400_BAD_REQUEST)


class SubmitForReviewView(APIView):
    permission_classes = [IsAuthenticated, StaffPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("pack_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("supplier_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True)
        ],
        responses={200: "pack submitted successfully!", 400: "pack already submitted!", 404: "pack not found!"})
    def patch(request):
        """This function handles pack submission to admin for review"""
        request_id = request.GET.get("request_id")
        pack_id = request.GET.get("pack_id")
        pack_title = request.GET.get("pack_title")
        pack_type = request.GET.get("pack_type")
        supplier_id = request.GET.get("supplier_id")

        if pack_type in PackTypes.list():
            submission = PackSubmissions.objects.select_related("pack", "supplier").filter(
                id=request_id, pack__id=pack_id,
                pack__title=pack_title,
                supplier__id=supplier_id,
                pack_type=pack_type).first()
            if submission:
                if not (submission.status in [SubmissionStatus.UPLOADED, SubmissionStatus.PROCESS]):
                    return Response({"detail": "pack already submitted!"}, status=status.HTTP_400_BAD_REQUEST)
                # if sum(1 for file in submission.pack.audio_files.all() if file.status == FileStatus.APPROVED) < 100:
                #     return Response({"detail": "pack should have at least 100 approved file!"},
                #                     status=status.HTTP_400_BAD_REQUEST)
                submission.status = SubmissionStatus.SUBMITTED
                submission.save(update_fields=["status"])
                return Response({"detail": "pack submitted successfully!"}, status=status.HTTP_200_OK)
            return Response({"detail": "pack not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid pack type"}, status=status.HTTP_400_BAD_REQUEST)


class ViewSubmittedPacksView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("pack_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING),
            openapi.Parameter("pack_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING)
        ],
        responses={200: ViewPacksSerializer(many=True)})
    def get(request):
        """This function handles pack-submissions"""
        pack_id = request.GET.get("pack_id")
        pack_type = request.GET.get("pack_type")
        queryset = {}
        if pack_id:
            queryset["pk"] = pack_id
        if pack_type in PackTypes.list():
            if pack_type:
                queryset['pack_type'] = pack_type
            pack = PackSubmissions.objects.select_related("pack", "supplier"). \
                filter(**queryset, status=SubmissionStatus.SUBMITTED)
        else:
            pack = PackSubmissions.objects.select_related("pack", "supplier"). \
                filter(**queryset, status=SubmissionStatus.SUBMITTED)
        view_packs_serializer = ViewPacksSerializer(pack, many=True)
        return Response({"detail": view_packs_serializer.data}, status=status.HTTP_200_OK)


class ApprovePackView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("pack_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("supplier_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True)
        ],
        responses={200: "pack approved successfully!", 400: "cannot approve pack!", 404: "pack not found!"})
    def patch(request):
        """This function handles pack approval from admin"""
        request_id = request.GET.get("request_id")
        pack_id = request.GET.get("pack_id")
        pack_title = request.GET.get("pack_title")
        pack_type = request.GET.get("pack_type")
        supplier_id = request.GET.get("supplier_id")

        if pack_type in PackTypes.list():
            submission = PackSubmissions.objects.select_related("pack", "supplier").filter(
                id=request_id, pack__id=pack_id,
                pack__title=pack_title,
                supplier__id=supplier_id,
                pack_type=pack_type).first()
            if submission:
                if submission.status != SubmissionStatus.SUBMITTED:
                    return Response({"detail": "cannot approve pack!"}, status=status.HTTP_400_BAD_REQUEST)
                submission.status = SubmissionStatus.APPROVED
                submission.save(update_fields=["status"])
                return Response({"detail": "pack approved successfully!"}, status=status.HTTP_200_OK)
            return Response({"detail": "pack not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid pack type"}, status=status.HTTP_400_BAD_REQUEST)


class RejectPackView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("pack_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("pack_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("supplier_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True)
        ],
        responses={200: "pack rejected successfully!", 400: "cannot reject pack!", 404: "pack not found!"})
    def patch(request):
        """This function handles pack rejection from admin"""
        request_id = request.GET.get("request_id")
        pack_id = request.GET.get("pack_id")
        pack_title = request.GET.get("pack_title")
        pack_type = request.GET.get("pack_type")
        supplier_id = request.GET.get("supplier_id")

        if pack_type in PackTypes.list():
            submission = PackSubmissions.objects.select_related("pack", "supplier").filter(
                id=request_id, pack__id=pack_id,
                pack__title=pack_title,
                supplier__id=supplier_id,
                pack_type=pack_type).first()
            if submission:
                if submission.status in [SubmissionStatus.UPLOADED, SubmissionStatus.PROCESS]:
                    return Response({"detail": "cannot reject pack!"}, status=status.HTTP_400_BAD_REQUEST)
                submission.status = SubmissionStatus.REJECTED
                submission.save(update_fields=["status"])
                return Response({"detail": "pack rejected successfully!"}, status=status.HTTP_200_OK)
            return Response({"detail": "pack not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid pack type"}, status=status.HTTP_400_BAD_REQUEST)
