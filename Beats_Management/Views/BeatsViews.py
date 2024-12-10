from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Beats_Management.Serializers import BeatSubmissionsSerializer, ViewBeatsSerializer, BeatRevisedAudioFileSerializer
from Beats_Management.models import BeatsSubmissions
from Utilities.Enums import BeatTypes, SubmissionStatus, FileStatus, Boolean
from Utilities.Permissions import AdminPermissions, StaffPermissions, SupplierPermissions


class BeatsSubmissionsView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions | SupplierPermissions]

    @staticmethod
    @swagger_auto_schema(request_body=BeatSubmissionsSerializer(),
                         responses={200: "beat submitted successfully"})
    def post(request):
        """This function handles beat-submissions"""
        try:
            with transaction.atomic():
                beats_submissions_serializer = BeatSubmissionsSerializer(data=request.data,
                                                                         context={"supplier": request.user})
                beats_submissions_serializer.is_valid()

                if beats_submissions_serializer.errors:
                    return Response({"detail": beats_submissions_serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

                beats_submissions_serializer.save()
                return Response({"detail": "beat submitted successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ViewBeatsView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions | StaffPermissions | SupplierPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("beat_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING),
            openapi.Parameter("beat_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING)
        ],
        responses={200: ViewBeatsSerializer(many=True), 404: "beat not found!"})
    def get(request):
        """This function handles beat-submissions"""
        beat_id = request.GET.get("beat_id")
        beat_type = request.GET.get("beat_type")
        if beat_type in BeatTypes.list():
            queryset = {}
            if beat_id:
                queryset["pk"] = beat_id
            if beat_type:
                queryset['beat_type'] = beat_type
            if request.user.is_supplier or request.user.is_admin:
                queryset['supplier'] = request.user
            beat = BeatsSubmissions.objects.select_related("beat", "supplier").filter(**queryset)
            view_beats_serializer = ViewBeatsSerializer(beat, many=True)
            return Response({"detail": view_beats_serializer.data}, status=status.HTTP_200_OK)
        return Response({"detail": "invalid beat type"}, status=status.HTTP_404_NOT_FOUND)


class SendRevisionBeatsView(APIView):
    permission_classes = [IsAuthenticated, StaffPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("beat_type", in_=openapi.IN_QUERY,
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
        responses={200: ViewBeatsSerializer(many=True), 400: "cannot send revision", 404: "beat not found!"})
    def patch(request):
        """This function handles beat-revisions"""
        request_id = request.GET.get("request_id")
        beat_id = request.GET.get("beat_id")
        beat_title = request.GET.get("beat_title")
        beat_type = request.GET.get("beat_type")
        supplier_id = request.GET.get("supplier_id")
        file_id = request.GET.get("file_id")
        file_name = request.GET.get("file_name")
        file_revision_message = request.GET.get("file_revision_message")
        is_demo_file = request.GET.get("is_demo_file")

        if beat_type in BeatTypes.list():
            submission = BeatsSubmissions.objects.select_related("beat", "beat__demo_file", "supplier").filter(
                id=request_id, beat__id=beat_id,
                beat__title=beat_title,
                supplier__id=supplier_id,
                beat_type=beat_type).first()
            if submission:
                if not (submission.status in [SubmissionStatus.UPLOADED, SubmissionStatus.PROCESS]):
                    return Response({"detail": "cannot send revisions!"}, status=status.HTTP_400_BAD_REQUEST)
                if Boolean.get_bool(is_demo_file):
                    if str(submission.beat.demo_file.file.id) != file_id or \
                            submission.beat.demo_file.file.file_name != file_name:
                        return Response({"detail": "file not found!"}, status=status.HTTP_404_NOT_FOUND)
                    file = submission.beat.demo_file
                else:
                    audio_file = submission.beat.audio_files.select_related("file"). \
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
            return Response({"detail": "beat not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid beat type"}, status=status.HTTP_400_BAD_REQUEST)


class ResolveRevisionBeatsView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions | SupplierPermissions]

    @staticmethod
    @swagger_auto_schema(
        request_body=BeatRevisedAudioFileSerializer(),
        responses={200: "beat revised successfully", 404: "beat submission does not exist!"})
    def post(request):
        """This function resolve beat-revisions"""
        try:
            with transaction.atomic():
                beats_revision_serializer = BeatRevisedAudioFileSerializer(data=request.data,
                                                                       context={"user": request.user})
                beats_revision_serializer.is_valid()

                if beats_revision_serializer.errors:
                    return Response({"detail": beats_revision_serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

                beats_revision_serializer.save()
                return Response({"detail": "beat revised successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ApproveRevisionBeatsView(APIView):
    permission_classes = [IsAuthenticated, StaffPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("beat_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("supplier_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("file_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("file_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("is_demo_file", in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=True)
        ],
        responses={200: "file approved successfully!", 400: "cannot approve file", 404: "beat not found!"})
    def patch(request):
        """This function handles beat-approval"""
        request_id = request.GET.get("request_id")
        beat_id = request.GET.get("beat_id")
        beat_title = request.GET.get("beat_title")
        beat_type = request.GET.get("beat_type")
        supplier_id = request.GET.get("supplier_id")
        file_id = request.GET.get("file_id")
        file_name = request.GET.get("file_name")
        is_demo_file = request.GET.get("is_demo_file")

        if beat_type in BeatTypes.list():
            submission = BeatsSubmissions.objects.select_related("beat", "beat__demo_file", "supplier").filter(
                id=request_id, beat__id=beat_id,
                beat__title=beat_title,
                supplier__id=supplier_id,
                beat_type=beat_type).first()
            if submission:
                if not (submission.status in [SubmissionStatus.UPLOADED, SubmissionStatus.PROCESS]):
                    return Response({"detail": "cannot approve file!"}, status=status.HTTP_400_BAD_REQUEST)

                if Boolean.get_bool(is_demo_file):
                    if str(submission.beat.demo_file.file.id) != file_id or \
                            submission.beat.demo_file.file.file_name != file_name:
                        return Response({"detail": "file not found!"}, status=status.HTTP_404_NOT_FOUND)
                    file = submission.beat.demo_file
                else:
                    audio_file = submission.beat.audio_files.select_related("file"). \
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
            return Response({"detail": "beat not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid beat type"}, status=status.HTTP_400_BAD_REQUEST)


class RejectRevisionBeatsView(APIView):
    permission_classes = [IsAuthenticated, StaffPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("beat_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("supplier_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("file_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("file_name", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("is_demo_file", in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=True)
        ],
        responses={200: "file rejected successfully!", 400: "cannot approve file", 404: "beat not found!"})
    def patch(request):
        """This function handles beat-rejection"""
        request_id = request.GET.get("request_id")
        beat_id = request.GET.get("beat_id")
        beat_title = request.GET.get("beat_title")
        beat_type = request.GET.get("beat_type")
        supplier_id = request.GET.get("supplier_id")
        file_id = request.GET.get("file_id")
        file_name = request.GET.get("file_name")
        is_demo_file = request.GET.get("is_demo_file")

        if beat_type in BeatTypes.list():
            submission = BeatsSubmissions.objects.select_related("beat", "beat__demo_file", "supplier").filter(
                id=request_id, beat__id=beat_id,
                beat__title=beat_title,
                supplier__id=supplier_id,
                beat_type=beat_type).first()
            if submission:
                if not (submission.status in [SubmissionStatus.UPLOADED, SubmissionStatus.PROCESS]):
                    return Response({"detail": "cannot approve file!"}, status=status.HTTP_400_BAD_REQUEST)

                if Boolean.get_bool(is_demo_file):
                    if str(submission.beat.demo_file.file.id) != file_id or \
                            submission.beat.demo_file.file.file_name != file_name:
                        return Response({"detail": "file not found!"}, status=status.HTTP_404_NOT_FOUND)
                    file = submission.beat.demo_file
                else:
                    audio_file = submission.beat.audio_files.select_related("file"). \
                        filter(file__id=file_id, file__file_name=file_name).first()
                    if not audio_file:
                        return Response({"detail": "file not found!"}, status=status.HTTP_404_NOT_FOUND)
                    file = audio_file

                file.status = FileStatus.REJECTED
                file.save(update_fields=["status"])
                file.status = SubmissionStatus.PROCESS
                file.save(update_fields=["status"])
                return Response({"detail": "file rejected successfully!"}, status=status.HTTP_200_OK)
            return Response({"detail": "beat not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid beat type"}, status=status.HTTP_400_BAD_REQUEST)


class BeatSubmitForReviewView(APIView):
    permission_classes = [IsAuthenticated, StaffPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("beat_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("supplier_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True)
        ],
        responses={200: "beat submitted successfully!", 400: "beat already submitted!", 404: "beat not found!"})
    def patch(request):
        """This function handles beat submission to admin for review"""
        request_id = request.GET.get("request_id")
        beat_id = request.GET.get("beat_id")
        beat_title = request.GET.get("beat_title")
        beat_type = request.GET.get("beat_type")
        supplier_id = request.GET.get("supplier_id")

        if beat_type in BeatTypes.list():
            submission = BeatsSubmissions.objects.select_related("beat", "supplier").filter(
                id=request_id, beat__id=beat_id,
                beat__title=beat_title,
                supplier__id=supplier_id,
                beat_type=beat_type).first()
            if submission:
                if not (submission.status in [SubmissionStatus.UPLOADED, SubmissionStatus.PROCESS]):
                    return Response({"detail": "beat already submitted!"}, status=status.HTTP_400_BAD_REQUEST)
                # if sum(1 for file in submission.beat.audio_files.all() if file.status == FileStatus.APPROVED) < 100:
                #     return Response({"detail": "beat should have at least 100 approved file!"},
                #                     status=status.HTTP_400_BAD_REQUEST)
                submission.status = SubmissionStatus.SUBMITTED
                submission.save(update_fields=["status"])
                return Response({"detail": "beat submitted successfully!"}, status=status.HTTP_200_OK)
            return Response({"detail": "beat not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid beat type"}, status=status.HTTP_400_BAD_REQUEST)


class ViewSubmittedBeatsView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("beat_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING),
            openapi.Parameter("beat_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING)
        ],
        responses={200: ViewBeatsSerializer(many=True)})
    def get(request):
        """This function handles beat-submissions"""
        beat_id = request.GET.get("beat_id")
        beat_type = request.GET.get("beat_type")
        queryset = {}
        if beat_id:
            queryset["pk"] = beat_id
        if beat_type in BeatTypes.list():
            if beat_type:
                queryset['beat_type'] = beat_type
            beat = BeatsSubmissions.objects.select_related("beat", "supplier"). \
                filter(**queryset, status=SubmissionStatus.SUBMITTED)
        else:
            beat = BeatsSubmissions.objects.select_related("beat", "supplier"). \
                filter(**queryset, status=SubmissionStatus.SUBMITTED)
        view_beats_serializer = ViewBeatsSerializer(beat, many=True)
        return Response({"detail": view_beats_serializer.data}, status=status.HTTP_200_OK)


class ApproveBeatView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("beat_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("supplier_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True)
        ],
        responses={200: "beat approved successfully!", 400: "cannot approve beat!", 404: "beat not found!"})
    def patch(request):
        """This function handles beat approval from admin"""
        request_id = request.GET.get("request_id")
        beat_id = request.GET.get("beat_id")
        beat_title = request.GET.get("beat_title")
        beat_type = request.GET.get("beat_type")
        supplier_id = request.GET.get("supplier_id")

        if beat_type in BeatTypes.list():
            submission = BeatsSubmissions.objects.select_related("beat", "supplier").filter(
                id=request_id, beat__id=beat_id,
                beat__title=beat_title,
                supplier__id=supplier_id,
                beat_type=beat_type).first()
            if submission:
                if submission.status != SubmissionStatus.SUBMITTED:
                    return Response({"detail": "cannot approve beat!"}, status=status.HTTP_400_BAD_REQUEST)
                submission.status = SubmissionStatus.APPROVED
                submission.save(update_fields=["status"])
                return Response({"detail": "beat approved successfully!"}, status=status.HTTP_200_OK)
            return Response({"detail": "beat not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid beat type"}, status=status.HTTP_400_BAD_REQUEST)


class RejectBeatView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("request_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter("beat_title", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("beat_type", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("supplier_id", in_=openapi.IN_QUERY,
                              type=openapi.TYPE_NUMBER, required=True)
        ],
        responses={200: "beat rejected successfully!", 400: "cannot reject beat!", 404: "beat not found!"})
    def patch(request):
        """This function handles beat rejection from admin"""
        request_id = request.GET.get("request_id")
        beat_id = request.GET.get("beat_id")
        beat_title = request.GET.get("beat_title")
        beat_type = request.GET.get("beat_type")
        supplier_id = request.GET.get("supplier_id")

        if beat_type in BeatTypes.list():
            submission = BeatsSubmissions.objects.select_related("beat", "supplier").filter(
                id=request_id, beat__id=beat_id,
                beat__title=beat_title,
                supplier__id=supplier_id,
                beat_type=beat_type).first()
            if submission:
                if submission.status in [SubmissionStatus.UPLOADED, SubmissionStatus.PROCESS]:
                    return Response({"detail": "cannot reject beat!"}, status=status.HTTP_400_BAD_REQUEST)
                submission.status = SubmissionStatus.REJECTED
                submission.save(update_fields=["status"])
                return Response({"detail": "beat rejected successfully!"}, status=status.HTTP_200_OK)
            return Response({"detail": "beat not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "invalid beat type"}, status=status.HTTP_400_BAD_REQUEST)
