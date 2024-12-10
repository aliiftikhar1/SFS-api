from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password

from rest_framework import serializers

from User_Management.models import User

from Utilities.EmailsHandler import EmailsHandler
from Utilities.Validators.InputValidator import InputValidator


def validate_new_and_confirm_password(attrs):
    new_password = attrs.get("new_password")
    confirm_password = attrs.pop("confirm_password")

    if not InputValidator(new_password).is_valid():
        raise serializers.ValidationError("new_password is required.")

    if not InputValidator(confirm_password).is_valid():
        raise serializers.ValidationError("confirm_password is required.")

    if new_password != confirm_password:
        raise serializers.ValidationError(
            "new password and confirm password does not match."
        )


class UserPasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        write_only=True,
        error_messages={
            "required": "old_password is required",
            "blank": "old_password cannot be blank",
        },
    )
    new_password = serializers.CharField(
        error_messages={
            "required": "new_password is required",
            "blank": "new_password cannot be blank",
        }
    )
    confirm_password = serializers.CharField(
        error_messages={
            "required": "confirm_password is required",
            "blank": "password cannot be blank",
        }
    )

    class Meta:
        model = User
        fields = ("old_password", "new_password", "confirm_password")

    def validate(self, attrs):
        old_password = attrs.get("old_password")

        if not InputValidator(old_password).is_valid():
            raise serializers.ValidationError("old_password is required.")

        validate_new_and_confirm_password(attrs)

        user = self.instance

        if not check_password(old_password, user.password):
            raise serializers.ValidationError("old password is not valid.")

        return attrs

    def update(self, instance, validated_data):
        with transaction.atomic():
            new_password = validated_data.pop("new_password")
            validated_data["password"] = make_password(new_password)
            super().update(instance=instance, validated_data=validated_data)
            EmailsHandler(to_user=instance).set_update_email(update="Password").send()
            return instance


class UserResetPasswordSerializer(serializers.ModelSerializer):
    token = serializers.CharField(
        error_messages={
            "required": "token is required",
            "blank": "token cannot be blank",
        }
    )
    new_password = serializers.CharField(
        error_messages={
            "required": "new_password is required",
            "blank": "new_password cannot be blank",
        }
    )
    confirm_password = serializers.CharField(
        error_messages={
            "required": "confirm_password is required",
            "blank": "password cannot be blank",
        }
    )

    class Meta:
        model = User
        fields = ("token", "new_password", "confirm_password")

    def validate(self, attrs):
        token = attrs.pop("token")
        _, email, _, _ = EmailsHandler.split_token(token)
        user = User.objects.filter(
            email=email, is_deleted=False, is_active=True
        ).first()

        if not user:
            raise serializers.ValidationError("invalid token")

        validate_new_and_confirm_password(attrs)
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        instance = validated_data.pop("user")
        new_password = validated_data.pop("new_password")

        with transaction.atomic():
            validated_data["password"] = make_password(new_password)
            super().update(instance=instance, validated_data=validated_data)
            EmailsHandler(to_user=instance).set_update_email(update="Password").send()
            return instance
