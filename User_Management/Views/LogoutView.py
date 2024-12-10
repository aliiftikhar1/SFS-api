from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Utilities.Enums.UserTypes import UserType
from Utilities.Permissions.AdminPermissions import AdminPermissions
from Utilities.Permissions.MemberPermissions import MemberPermissions
from Utilities.Permissions.StaffPermissions import StaffPermissions
from Utilities.Permissions.SupplierPermissions import SupplierPermissions


class LogoutView(APIView):
    permission_classes = [
        IsAuthenticated,
        (
                AdminPermissions
                | StaffPermissions
                | SupplierPermissions
                | MemberPermissions
        ),
    ]

    @staticmethod
    @swagger_auto_schema(
        responses={
            200: "user logged out successfully!",
            400: "an error occurred while logout!",
        }
    )
    def get(request):
        """This function logout the current User."""
        if request.user.usertype in UserType.list():
            request.user.auth_token = None
            request.user.save(update_fields=["auth_token"])
            return Response(
                {"detail": "user logged out successfully!"}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "an error occurred while logout!"},
            status=status.HTTP_400_BAD_REQUEST,
        )
