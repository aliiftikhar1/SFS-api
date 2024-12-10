from django.db import transaction

from rest_framework import serializers

from User_Management.models import User, Member

from Utilities.EmailsHandler import EmailsHandler
from Utilities.Validators.InputValidator import InputValidator


class VerifyMemberSignUpSerializer(serializers.Serializer):
    otp = serializers.CharField(
        error_messages={"required": "otp is required", "blank": "otp cannot be blank"}
    )
    token = serializers.CharField(
        error_messages={
            "required": "token is required",
            "blank": "token cannot be blank",
        }
    )

    class Meta:
        fields = ("otp", "token")

    def validate(self, attrs):
        otp = attrs.get("otp")
        token = attrs.get("token")

        if not InputValidator(otp).is_valid():
            raise serializers.ValidationError("otp is required.")

        if not InputValidator(token).is_valid():
            raise serializers.ValidationError("token is required.")

        result = EmailsHandler.validate_confirmation_email(otp, token)

        if isinstance(result, str):
            raise serializers.ValidationError("otp is invalid.")

        return result

    def create(self, validated_data):
        with transaction.atomic():
            username = validated_data.get("username")
            email = validated_data.get("email")
            password = validated_data.get("password")

            user = User.objects.create(email=email, password=password, verified=True)
            member = Member.objects.create(
                member_user=user, username=username, name="Member"
            )

            EmailsHandler(to_user=user).set_welcome_email().send()
            return member
