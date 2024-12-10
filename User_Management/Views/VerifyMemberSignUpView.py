from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from User_Management.Serializers.VerifyMemberSignUpSerializer import (
    VerifyMemberSignUpSerializer,
)
from Utilities import extract_error_messages


class VerifyMemberSignUpView(APIView):
    @staticmethod
    @swagger_auto_schema(
        request_body=VerifyMemberSignUpSerializer(),
        responses={200: "account created successfully!"},
    )
    def post(request):
        """This function performs email verification functionality for users signup."""
        signup_serializer = VerifyMemberSignUpSerializer(data=request.data)
        signup_serializer.is_valid()
        if signup_serializer.errors:
            return Response(
                {"detail": extract_error_messages(signup_serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        signup_serializer.save()
        return Response(
            {"detail": "account created successfully!"}, status=status.HTTP_201_CREATED
        )
