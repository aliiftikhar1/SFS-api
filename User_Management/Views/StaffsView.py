from datetime import datetime

from django.db import transaction

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from User_Management.models import AdminOrStaff
from User_Management.Serializers.StaffsModelSerializer import (
    StaffsSerializer,
    StaffSerializer,
)
from Utilities import extract_error_messages

from Utilities.Enums.UserTypes import UserType
from Utilities.Permissions.AdminPermissions import AdminPermissions


class StaffsView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: StaffsSerializer(many=True)})
    def get(request):
        """This function return the staff."""
        try:
            staffs = AdminOrStaff.objects.select_related("admin_user").filter(
                admin_user__usertype=UserType.STAFF.value, admin_user__is_deleted=False
            )

            staffs_serializer = StaffsSerializer(staffs, many=True)
            return Response(
                {"detail": staffs_serializer.data}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StaffView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "staff_id",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                required=True,
            )
        ],
        responses={200: StaffsSerializer(), 404: "staff member not found"},
    )
    def get(request):
        """This function return the staff base on their id's."""
        staff_id = request.GET.get("staff_id")
        staff = (
            AdminOrStaff.objects.select_related("admin_user")
            .filter(
                admin_user_id=staff_id,
                admin_user__usertype=UserType.STAFF.value,
                admin_user__is_deleted=False,
            )
            .first()
        )
        if staff:
            staff_serializer = StaffsSerializer(staff)
            return Response(
                {"detail": staff_serializer.data}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "staff member not found"}, status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="string"),
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="string"
                ),
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="string"),
                "confirm_email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="string"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="string"
                ),
                "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="string"
                ),
            },
        ),
        responses={200: "staff member created successfully"},
    )
    def post(request):
        """This function creates the new staff members with given data."""
        staff_serializer = StaffSerializer(data=request.data)
        staff_serializer.is_valid()

        if staff_serializer.errors:
            return Response(
                {"detail": extract_error_messages(staff_serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        staff_serializer.save()
        return Response(
            {"detail": f"staff member created successfully"}, status=status.HTTP_200_OK
        )

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "email", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                "username",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: "staff member deleted successfully",
            404: "staff member not found!",
        },
    )
    def delete(request):
        """This function delete the staff members based on their email's and username"""
        email = request.GET.get("email")
        username = request.GET.get("username")

        staff = (
            AdminOrStaff.objects.select_related("admin_user")
            .filter(username=username, admin_user__email=email)
            .first()
        )

        if staff:
            with transaction.atomic():
                staff.admin_user.is_deleted = True
                staff.admin_user.is_active = False
                staff.admin_user.deleted_at = datetime.now()
                staff.admin_user.save(
                    update_fields=["is_deleted", "is_active", "deleted_at"]
                )
                staff.save()
            return Response(
                {"detail": f"staff member deleted successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "staff member not found"}, status=status.HTTP_404_NOT_FOUND
        )
