from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from User_Management.Serializers.UserAccountDeletionSerializer import UserVerifyAccountDeletionOTPSerializer, \
    UserAccountDeletionSerializer
from Utilities import extract_error_messages
from Utilities.Permissions.AdminPermissions import AdminPermissions
from Utilities.Permissions.MemberPermissions import MemberPermissions
from Utilities.Permissions.StaffPermissions import StaffPermissions
from Utilities.Permissions.SupplierPermissions import SupplierPermissions


class UserProfileDeleteView(APIView):
    permission_classes = [
        IsAuthenticated,
        (
                AdminPermissions
                | StaffPermissions
                | MemberPermissions
                | SupplierPermissions
        ),
    ]

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
        responses={200: "{'token': 'token'}", 400: "no such user exist with this email and username."}
    )
    def delete(request):
        """This function sends otp the Users based on their email's and username"""
        account_deletion_serializer = UserAccountDeletionSerializer(instance=request.user, data=request.GET)
        account_deletion_serializer.is_valid()

        if account_deletion_serializer.errors:
            return Response(
                {"detail": extract_error_messages(account_deletion_serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = account_deletion_serializer.save()
        return Response(
            {"detail": token}, status=status.HTTP_200_OK
        )


class UserProfileVerifyDeletionView(APIView):
    permission_classes = [
        IsAuthenticated,
        (
                AdminPermissions
                | StaffPermissions
                | MemberPermissions
                | SupplierPermissions
        ),
    ]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "otp", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                "token", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
            ),
        ],
        responses={200: "account deleted successfully", 404: "could not delete user... try again!!!"},
    )
    def delete(request):
        """This function delete the Users based on their email's and username"""
        account_deletion_verify_serializer = UserVerifyAccountDeletionOTPSerializer(instance=request.user,
                                                                                    data=request.GET)
        account_deletion_verify_serializer.is_valid()

        if account_deletion_verify_serializer.errors:
            return Response(
                {"detail": extract_error_messages(account_deletion_verify_serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        account_deletion_verify_serializer.save()
        return Response(
            {"detail": f"account deleted successfully"}, status=status.HTTP_200_OK
        )
