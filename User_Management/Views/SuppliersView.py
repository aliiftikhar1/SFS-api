from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from User_Management.Serializers.SuppliersModelSerializer import (
    SupplierApplySerializer,
    SuppliersInProcessSerializer,
    SuppliersDetailsSerializer,
    SuppliersStatusSerializer,
    SupplierInterviewSerializer,
    SupplierUploadContractSerializer,
    SupplierUpdateContractSerializer,
    SuppliersApprovedSerializer,
)
from User_Management.models import Requests
from Utilities import extract_error_messages
from Utilities.Enums.Boolean import Boolean
from Utilities.Enums.RequestStatus import RequestStatus
from Utilities.Permissions.AdminPermissions import AdminPermissions


class SupplierApplyView(APIView):
    @staticmethod
    def post(request):
        """This function creates applications of the new suppliers with given data."""
        supplier_serializer = SupplierApplySerializer(data=request.data)
        supplier_serializer.is_valid()
        if supplier_serializer.errors:
            return Response(
                {"detail": extract_error_messages(supplier_serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        supplier_serializer.save()
        return Response(
            {"detail": f"supplier request submitted received"},
            status=status.HTTP_200_OK,
        )


class SupplierDetailView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "email", type=openapi.TYPE_STRING, in_=openapi.IN_QUERY, required=True
            ),
            openapi.Parameter(
                "username",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                required=True,
            ),
        ],
        responses={200: "", 400: "request not found"},
    )
    def get(request):
        """This function creates applications of the new suppliers with given data."""
        email = request.GET.get("email")
        username = request.GET.get("username")
        request_details = (
            Requests.objects.select_related(
                "supplier",
                "supplier__artist",
                "supplier__supplier_user",
                "supplier__artist__content_info",
            )
            .filter(supplier__supplier_user__email=email, supplier__username=username)
            .first()
        )
        if request_details:
            requests_serializer = SuppliersDetailsSerializer(request_details)
            return Response(
                {"detail": requests_serializer.data}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "request not found"}, status=status.HTTP_404_NOT_FOUND
        )


class ContractUploadSupplierView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        request_body=SupplierUploadContractSerializer(),
        responses={200: "contract uploaded successfully"},
    )
    def post(request):
        """This function uploads contract of the new suppliers."""
        supplier_upload_contract_serializer = SupplierUploadContractSerializer(
            data=request.data
        )
        supplier_upload_contract_serializer.is_valid()
        if supplier_upload_contract_serializer.errors:
            return Response(
                {
                    "detail": extract_error_messages(
                        supplier_upload_contract_serializer.errors
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        supplier_upload_contract_serializer.save()
        return Response(
            {"detail": "contract uploaded successfully"}, status=status.HTTP_200_OK
        )


class ContractUpdateSupplierView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        request_body=SupplierUpdateContractSerializer(),
        responses={200: "contract updated successfully"},
    )
    def post(request):
        """This function updates contract of the new suppliers."""
        supplier_update_contract_serializer = SupplierUpdateContractSerializer(
            data=request.data
        )
        supplier_update_contract_serializer.is_valid()
        if supplier_update_contract_serializer.errors:
            return Response(
                {
                    "detail": extract_error_messages(
                        supplier_update_contract_serializer.errors
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        supplier_update_contract_serializer.save()
        return Response(
            {"detail": "contract updated successfully"}, status=status.HTTP_200_OK
        )


class SupplierInterviewView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        request_body=SupplierInterviewSerializer(),
        responses={200: "interview details set successfully"},
    )
    def post(request):
        """This function sets interview of suppliers with given data."""
        supplier_interview_serializer = SupplierInterviewSerializer(data=request.data)
        supplier_interview_serializer.is_valid()
        if supplier_interview_serializer.errors:
            return Response(
                {
                    "detail": extract_error_messages(
                        supplier_interview_serializer.errors
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        supplier_interview_serializer.save()
        return Response(
            {"detail": "interview details set successfully"}, status=status.HTTP_200_OK
        )


class SupplierStatusView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "hidden",
                default=False,
                type=openapi.TYPE_BOOLEAN,
                in_=openapi.IN_QUERY,
                required=True,
            ),
            openapi.Parameter(
                "status", type=openapi.TYPE_STRING, in_=openapi.IN_QUERY, required=True
            ),
        ],
        responses={
            200: SuppliersStatusSerializer(many=True)
            or SuppliersInProcessSerializer(many=True)
            or SuppliersApprovedSerializer(many=True),
            400: "Invalid request status",
        },
    )
    def get(request):
        """This function return the supplier's requests based on their statuses.
        Statuses:
            APPLIED = "Applied"
            IN_PROCESS = "In Process"
            PENDING = "Pending"
            APPROVED = "Approved"
            DECLINED = "Declined"
        """

        hidden = request.GET.get("hidden")
        request_status = request.GET.get("status")

        if hidden not in Boolean.list():
            return Response(
                {"detail": "hidden should be a boolean"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hidden = Boolean.get_bool(hidden)

        if request_status in RequestStatus.list():
            requests = Requests.objects.select_related(
                "supplier", "supplier__artist", "supplier__supplier_user"
            ).filter(status=request_status, hidden=hidden)

            if request_status == RequestStatus.IN_PROCESS.value:
                requests_serializer = SuppliersInProcessSerializer(requests, many=True)
            elif request_status == RequestStatus.APPROVED.value:
                requests_serializer = SuppliersApprovedSerializer(requests, many=True)
            else:
                requests_serializer = SuppliersStatusSerializer(requests, many=True)
            return Response(
                {"detail": requests_serializer.data}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "Invalid request status"}, status=status.HTTP_400_BAD_REQUEST
        )


class HideSupplierView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "hide": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN, description="boolean"
                ),
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="string"),
            },
            required=["hide", "email"],
        ),
        responses={200: "request updated successfully", 400: "request not found"},
    )
    def put(request):
        """This function hides the supplier's requests."""
        email = request.data.get("email")
        hide = request.data.get("hide")

        request = (
            Requests.objects.select_related("supplier", "supplier__supplier_user")
            .filter(supplier__supplier_user__email=email)
            .first()
        )

        if request:
            with transaction.atomic():
                request.hidden = hide
                request.save(update_fields=["hidden"])
            return Response(
                {"detail": "request updated successfully"}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "request not found"}, status=status.HTTP_404_NOT_FOUND
        )


class DeclineSupplierView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="string"),
            },
            required=["email"],
        ),
        responses={200: "request updated successfully", 400: "request not found"},
    )
    def post(request):
        """This function declines the supplier's requests."""
        email = request.data.get("email")

        request = (
            Requests.objects.select_related("supplier", "supplier__supplier_user")
            .filter(supplier__supplier_user__email=email)
            .first()
        )

        if request:
            if request.status == RequestStatus.IN_PROCESS.value:
                with transaction.atomic():
                    request.status = RequestStatus.DECLINED.value
                    request.save(update_fields=["status"])
                return Response(
                    {"detail": "request updated successfully"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"detail": "request should be in process"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "request not found"}, status=status.HTTP_404_NOT_FOUND
        )


class ApproveSupplierView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="string"),
            },
            required=["email"],
        ),
        responses={200: "request updated successfully", 400: "request not found"},
    )
    def put(request):
        """This function approve the supplier's requests."""
        email = request.data.get("email")

        request = (
            Requests.objects.select_related("supplier", "supplier__supplier_user")
            .filter(supplier__supplier_user__email=email)
            .first()
        )

        if request:
            if request.status == RequestStatus.IN_PROCESS.value:
                with transaction.atomic():
                    request.status = RequestStatus.APPROVED.value
                    request.save(update_fields=["status"])
                return Response(
                    {"detail": "request updated successfully"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"detail": "request should be in process"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "request not found"}, status=status.HTTP_404_NOT_FOUND
        )
