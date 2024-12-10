from datetime import datetime

from django.db import transaction
from rest_framework import serializers

from Utilities import generate_otp
from Utilities.EmailsHandler import EmailsHandler
from Utilities.Validators.EmailValidator import EmailValidator
from Utilities.Validators.InputValidator import InputValidator


class UserAccountDeletionSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "required": "email is required",
            "blank": "email cannot be blank",
            "invalid": "enter a valid email",
        }
    )
    username = serializers.CharField(
        error_messages={
            "required": "username is required",
            "blank": "username cannot be blank"
        }
    )

    class Meta:
        fields = ("email", 'username')

    def validate(self, attrs):
        email = attrs.get("email")
        username = attrs.get("username")

        if not EmailValidator(email).is_valid():
            raise serializers.ValidationError("email is required.")
        if not InputValidator(username).is_valid():
            raise serializers.ValidationError("username is required.")

        if self.instance.get_user_details().username != username or self.instance.email != email:
            raise serializers.ValidationError("no such user exist with this email and username.")

        return attrs

    def update(self, instance, validated_data):
        with transaction.atomic():
            random_otp = generate_otp()
            sender = EmailsHandler(to_user=instance)
            sender.set_account_deletion_otp_email(otp=random_otp).send()
        return sender.token


class UserVerifyAccountDeletionOTPSerializer(serializers.Serializer):
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

        result = EmailsHandler.validate_verify_otp_email(otp, token, user=self.instance)

        if result != "valid":
            raise serializers.ValidationError(f"invalid {result}.")

        return attrs

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.is_deleted = True
            instance.is_active = False
            instance.deleted_at = datetime.now()
            instance.save(
                update_fields=["is_deleted", "is_active", "deleted_at"]
            )
            instance.save()
        return instance
