from django.db import transaction

from rest_framework import serializers

from User_Management.models import User
from Utilities import generate_otp

from Utilities.EmailsHandler import EmailsHandler
from Utilities.Validators.EmailValidator import EmailValidator
from Utilities.Validators.InputValidator import InputValidator


class UserForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "required": "email is required",
            "blank": "email cannot be blank",
            "invalid": "enter a valid email",
        }
    )

    class Meta:
        fields = ("email",)

    def validate(self, attrs):
        email = attrs.get("email")

        if not EmailValidator(email).is_valid():
            raise serializers.ValidationError("email is required.")

        user = User.objects.filter(email=email).first()

        if user is None:
            raise serializers.ValidationError("user with this does not exist.")

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.pop("user")

        with transaction.atomic():
            random_otp = generate_otp()
            sender = EmailsHandler(to_user=user)
            sender.set_verify_otp_email(otp=random_otp).send()
        return sender.token


class UserVerifyOTPSerializer(serializers.Serializer):
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

        result = EmailsHandler.validate_verify_otp_email(otp, token)

        if result != "valid":
            raise serializers.ValidationError(f"invalid {result}.")

        return attrs
