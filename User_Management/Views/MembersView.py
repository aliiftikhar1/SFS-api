from datetime import datetime

from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from User_Management.Serializers.MembersModelSerializer import (
    MembersSerializer,
    MemberSerializer,
)
from User_Management.models import Member
from Utilities import extract_error_messages
from Utilities.Enums.UserTypes import UserType
from Utilities.Permissions.AdminPermissions import AdminPermissions


class MembersView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(responses={200: MembersSerializer(many=True)})
    def get(request):
        """This function return the members."""
        try:
            members = Member.objects.select_related("member_user").filter(
                member_user__usertype=UserType.MEMBER.value,
                member_user__is_deleted=False,
            )
            members_serializer = MembersSerializer(members, many=True)
            return Response(
                {"detail": members_serializer.data}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MemberView(APIView):
    permission_classes = [IsAuthenticated, AdminPermissions]

    @staticmethod
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "member_id",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                required=True,
            )
        ],
        responses={200: MembersSerializer(), 404: "please provide valid user id!"},
    )
    def get(request):
        member_id = request.GET.get("member_id")
        """This function return the members base on their id's."""
        member = (
            Member.objects.select_related("member_user")
            .filter(
                member_user_id=member_id,
                member_user__usertype=UserType.MEMBER.value,
                member_user__is_deleted=False,
            )
            .first()
        )
        if member:
            member_serializer = MembersSerializer(member)
            return Response(
                {"detail": member_serializer.data}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "please provide valid member id!"},
            status=status.HTTP_404_NOT_FOUND,
        )

    @staticmethod
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="string"
                ),
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="string"),
                "confirm_email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="string"
                ),
                "country": openapi.Schema(type=openapi.TYPE_STRING, description="string"),
                "city_or_state": openapi.Schema(
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
        responses={200: "member created successfully"},
    )
    def post(request):
        """This function creates the new members with given data."""
        member_serializer = MemberSerializer(data=request.data)
        member_serializer.is_valid()
        if member_serializer.errors:
            return Response(
                {"detail": extract_error_messages(member_serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        member_serializer.save()
        return Response(
            {"detail": f"member created successfully"}, status=status.HTTP_200_OK
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
        responses={200: "user deleted successfully", 404: "member not found!"},
    )
    def delete(request):
        """This function delete the Users based on their id's and usertype"""
        email = request.GET.get("email")
        username = request.GET.get("username")

        member = (
            Member.objects.select_related("member_user")
            .filter(username=username, member_user__email=email)
            .first()
        )

        if member:
            with transaction.atomic():
                member.member_user.is_deleted = True
                member.member_user.is_active = False
                member.member_user.deleted_at = datetime.now()
                member.member_user.save(
                    update_fields=["is_deleted", "is_active", "deleted_at"]
                )
                member.save()
            return Response(
                {"detail": f"member deleted successfully"}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "member not found"}, status=status.HTTP_404_NOT_FOUND
        )
