from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from User_Management.Serializers.MemberSignUpSerializer import MemberSignUpSerializer
from Utilities import extract_error_messages


class MemberSignupView(APIView):
    @staticmethod
    @swagger_auto_schema(
        request_body=MemberSignUpSerializer(), responses={200: "{'token': 'token'}"}
    )
    def post(request):
        """This function performs sign up functionality for members."""
        signup_serializer = MemberSignUpSerializer(data=request.data)
        signup_serializer.is_valid()

        if signup_serializer.errors:
            return Response(
                {"detail": extract_error_messages(signup_serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, otp = signup_serializer.save()
        return Response({"detail": {"token": token}}, status=status.HTTP_200_OK)
