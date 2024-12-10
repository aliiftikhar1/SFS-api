from rest_framework import serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from User_Management.models import User
from Utilities.Enums.UserTypes import UserType


class SignInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        error_messages={
            "required": "email is required",
            "blank": "email cannot be blank",
            "invalid": "enter a valid email",
        }
    )
    password = serializers.CharField(
        error_messages={
            "required": "password is required",
            "blank": "password cannot be blank",
        }
    )
    usertype = serializers.ChoiceField(
        choices=UserType.choices,
        error_messages={
            "required": "usertype is required",
            "blank": "usertype cannot be blank",
        },
    )

    class Meta:
        model = User
        fields = ("email", "password", "usertype")

    def validate(self, attrs):
        usertype = attrs.get("usertype")

        if usertype not in UserType.list():
            raise serializers.ValidationError("invalid usertype")

        return attrs


class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField(
        error_messages={
            "required": "token is required",
            "blank": "token cannot be blank",
            "invalid": "enter a valid token",
        })
    email = serializers.CharField(
        error_messages={
            "required": "email is required",
            "blank": "email cannot be blank",
            "invalid": "email a valid token",
        })
    usertype = serializers.CharField(
        error_messages={
            "required": "usertype is required",
            "blank": "usertype cannot be blank",
            "invalid": "usertype a valid token",
        })

    class Meta:
        fields = ("token", "email", "usertype")

    def validate(self, attrs):
        token = attrs.get("token")
        email = attrs.get("email")
        usertype = attrs.get("usertype")

        if usertype not in UserType.list():
            raise serializers.ValidationError("invalid usertype")

        user = User.objects.filter(email=email, usertype=usertype).first()

        if not user:
            raise serializers.ValidationError("user not found")

        jwt_auth = JWTAuthentication()
        try:
            validated_token = jwt_auth.get_validated_token(token)
        except InvalidToken as e:
            raise serializers.ValidationError(e.default_detail.lower())

        user = jwt_auth.get_user(validated_token)

        if (
                not user.auth_token
        ) or (
                not all([user.is_active, (not user.is_deleted), user.auth_token == str(validated_token)])
        ):
            raise serializers.ValidationError("token is invalid or expired")

        return attrs
