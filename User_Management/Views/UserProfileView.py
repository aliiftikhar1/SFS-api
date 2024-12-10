from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from User_Management.Serializers.UserProfileSerializer import SupplierProfileSerializer, MemberProfileSerializer, \
    AdminOrStaffProfileSerializer
from Utilities import extract_error_messages
from Utilities.Permissions.AdminPermissions import AdminPermissions
from Utilities.Permissions.MemberPermissions import MemberPermissions
from Utilities.Permissions.StaffPermissions import StaffPermissions
from Utilities.Permissions.SupplierPermissions import SupplierPermissions


class UserProfileView(APIView):
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
        responses={200: (SupplierProfileSerializer() or MemberProfileSerializer() or AdminOrStaffProfileSerializer())
                   }
    )
    def get(request):
        """This function return the Users based on their usertype and id's."""
        profile_serializer = None
        user_details = request.user.get_user_details()
        if request.user.is_supplier:
            profile_serializer = SupplierProfileSerializer(user_details)
        elif request.user.is_member:
            profile_serializer = MemberProfileSerializer(user_details)
        elif request.user.is_admin or request.user.is_staff:
            profile_serializer = AdminOrStaffProfileSerializer(user_details)
        return Response({"detail": profile_serializer.data}, status=status.HTTP_200_OK)

    @staticmethod
    @swagger_auto_schema(
        request_body=SupplierProfileSerializer() or MemberProfileSerializer() or AdminOrStaffProfileSerializer(),
        responses={200: "profile updated successfully!", 400: 'username/email cannot be changed!'})
    def put(request):
        """This function updates the User's profile with given data."""
        email = request.data.get("email")
        username = request.data.get("username")

        user_details = request.user.get_user_details()

        if user_details.username == username and request.user.email == email:
            profile_serializer = None
            if request.user.is_supplier:
                profile_serializer = SupplierProfileSerializer(instance=user_details, data=request.data)
            elif request.user.is_member:
                profile_serializer = MemberProfileSerializer(instance=user_details, data=request.data)
            elif request.user.is_admin or request.user.is_staff:
                profile_serializer = AdminOrStaffProfileSerializer(instance=user_details, data=request.data)

            profile_serializer.is_valid()

            if profile_serializer.errors:
                return Response(
                    {"detail": extract_error_messages(profile_serializer.errors)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            profile_serializer.save()
            return Response(
                {"detail": f"profile updated successfully!"}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "username/email cannot be changed!"},
            status=status.HTTP_400_BAD_REQUEST,
        )
