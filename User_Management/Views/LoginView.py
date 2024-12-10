from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from User_Management.Serializers.SignInUserSerializer import SignInSerializer, VerifyTokenSerializer
from Utilities import extract_error_messages, generate_token
from Utilities.Enums.UserTypes import UserType


class LoginView(APIView):
    @staticmethod
    @swagger_auto_schema(
        request_body=SignInSerializer(),
        responses={
            200: '{"token": "token", "name": "name","email": "email",'
                 ' "profile_picture": "profile_picture"}',
            400: "Bad Request",
            404: "Email or password is not valid!",
        },
    )
    def post(request):
        """This function performs login functionality for users."""
        signin_serializer = SignInSerializer(data=request.data)
        signin_serializer.is_valid()

        if signin_serializer.errors:
            return Response(
                {"detail": extract_error_messages(signin_serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = signin_serializer.validated_data.get("email")
        password = signin_serializer.validated_data.get("password")
        usertype = signin_serializer.validated_data.get("usertype")

        user = authenticate(email=email, password=password, usertype=usertype)

        if user:
            token = generate_token(user)

            user.auth_token = token
            user.save(update_fields=["auth_token"])

            user_details = user.get_user_details()

            details = {
                "token": token,
                "email": user.email,
                "usertype": user.usertype,
                "profile_picture": user.profile_picture.url
                if user.profile_picture
                else None,
            }

            if UserType.is_supplier(usertype):
                details["name"] = f"{user_details.first_name} {user_details.last_name}"
            else:
                details["name"] = user_details.name

            return Response({"detail": details}, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Email or password is not valid!"},
            status=status.HTTP_404_NOT_FOUND,
        )


class VerifyTokenView(APIView):
    @staticmethod
    @swagger_auto_schema(
        request_body=VerifyTokenSerializer(),
        responses={
            200: 'token is valid',
            400: "token is invalid or expired" or "user not found" or "invalid usertype",
        },
    )
    def post(request):
        verify_token_serializer = VerifyTokenSerializer(data=request.data)
        verify_token_serializer.is_valid()

        if verify_token_serializer.errors:
            return Response(
                {"detail": extract_error_messages(verify_token_serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "token is valid"}, status=status.HTTP_200_OK)
