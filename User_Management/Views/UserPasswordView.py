from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from User_Management.Serializers.UserPasswordSerializer import UserPasswordSerializer
from Utilities import extract_error_messages
from Utilities.Permissions.AdminPermissions import AdminPermissions
from Utilities.Permissions.MemberPermissions import MemberPermissions
from Utilities.Permissions.StaffPermissions import StaffPermissions
from Utilities.Permissions.SupplierPermissions import SupplierPermissions


class UserPasswordView(APIView):
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
        request_body=UserPasswordSerializer(),
        responses={200: "password updated successfully!"},
    )
    def put(request):
        """This function performs change password functionality for users."""
        user_password_serializer = UserPasswordSerializer(
            instance=request.user, data=request.data, partial=True
        )
        user_password_serializer.is_valid()
        if user_password_serializer.errors:
            return Response(
                {"detail": extract_error_messages(user_password_serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_password_serializer.save()
        return Response(
            {"detail": f"password updated successfully!"}, status=status.HTTP_200_OK
        )
