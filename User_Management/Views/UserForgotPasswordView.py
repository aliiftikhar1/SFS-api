from drf_yasg.utils import swagger_auto_schema

from django.db import transaction

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from User_Management.Serializers.UserForgotPasswordSerializer import (
    UserForgotPasswordSerializer,
    UserVerifyOTPSerializer,
)
from User_Management.Serializers.UserPasswordSerializer import (
    UserResetPasswordSerializer,
)
from Utilities import extract_error_messages


class UserForgotPasswordView(APIView):
    @staticmethod
    @swagger_auto_schema(
        request_body=UserForgotPasswordSerializer(),
        responses={200: "{'token': 'token'}"},
    )
    def post(request):
        """This function performs forgot password functionality."""
        serializer = UserForgotPasswordSerializer(data=request.data)
        serializer.is_valid()
        if serializer.errors:
            return Response(
                {"detail": extract_error_messages(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = serializer.save()
        return Response({"detail": {"token": f"{token}"}}, status=status.HTTP_200_OK)


class UserVerifyOTPView(APIView):
    @staticmethod
    @swagger_auto_schema(
        request_body=UserVerifyOTPSerializer(), responses={200: "{'token': 'token'}"}
    )
    def post(request):
        """This function performs otp verification functionality."""
        verify_otp = UserVerifyOTPSerializer(data=request.data)
        verify_otp.is_valid()
        if verify_otp.errors:
            return Response(
                {"detail": extract_error_messages(verify_otp.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": f"otp verified successfully"}, status=status.HTTP_200_OK
        )


class UserResetPasswordView(APIView):
    @staticmethod
    @swagger_auto_schema(
        request_body=UserResetPasswordSerializer(),
        responses={200: "password updated successfully", 400: "invalid token"},
    )
    def post(request):
        """This function performs reset password functionality."""
        with transaction.atomic():
            user_reset_serializer = UserResetPasswordSerializer(data=request.data)
            user_reset_serializer.is_valid()
            if user_reset_serializer.errors:
                return Response(
                    {"detail": extract_error_messages(user_reset_serializer.errors)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_reset_serializer.save()
            return Response(
                {"detail": f"password updated successfully"}, status=status.HTTP_200_OK
            )
