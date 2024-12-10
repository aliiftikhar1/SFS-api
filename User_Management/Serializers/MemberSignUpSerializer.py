from django.db import transaction

from rest_framework import serializers

from User_Management.models import User, Member
from Utilities import generate_username, generate_otp

from Utilities.EmailsHandler import EmailsHandler
from Utilities.Validators.EmailValidator import EmailValidator
from Utilities.Validators.InputValidator import InputValidator


class MemberSignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "required": "email is required",
            "blank": "email cannot be blank",
            "invalid": "enter a valid email",
        }
    )
    password = serializers.CharField(
        write_only=True,
        error_messages={
            "required": "password is required",
            "blank": "password cannot be blank",
        },
    )
    confirm_password = serializers.CharField(
        error_messages={
            "required": "confirm_password is required",
            "blank": "password cannot be blank",
        }
    )

    class Meta:
        fields = ("email", "password", "confirm_password")

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password")

        if not EmailValidator(email=email).is_valid():
            raise serializers.ValidationError("email is not valid")

        if not InputValidator(password).is_valid():
            raise serializers.ValidationError("password is not valid")

        if not InputValidator(confirm_password).is_valid():
            raise serializers.ValidationError("confirm_password is not valid")

        if password != confirm_password:
            raise serializers.ValidationError(
                "password and confirm password does not match."
            )

        users = User.objects.all()
        if users.filter(email=email).first():
            raise serializers.ValidationError("email already exists")

        return attrs

    def create(self, validated_data):
        email = validated_data.pop("email")
        otp = generate_otp()
        password = validated_data.pop("password")
        username = generate_username(Member)

        user_details = (
            '{"email": "'
            + email
            + '", "password": "'
            + password
            + '","username": "'
            + username
            + '", "verified": true }'
        )

        with transaction.atomic():
            sender = EmailsHandler()
            sender = sender.set_confirmation_email(
                otp,
                email,
                user_details,
            )
            sender.send()
            return sender.token, otp
