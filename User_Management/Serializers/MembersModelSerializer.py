from django.db import transaction
from rest_framework import serializers

from User_Management.models import Member, User
from Utilities.EmailsHandler import EmailsHandler
from Utilities.Validators.EmailValidator import EmailValidator
from Utilities.Validators.InputValidator import InputValidator


class MembersSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField("get_profile_picture")
    username = serializers.SerializerMethodField("get_username")
    email = serializers.SerializerMethodField("get_email")
    is_active = serializers.SerializerMethodField("get_is_active")

    class Meta:
        model = Member
        fields = (
            "profile_picture",
            "username",
            "email",
            "is_active",
            "name",
            "country",
            "city_or_state",
            "description",
        )

    @staticmethod
    def get_profile_picture(obj):
        if obj.member_user.profile_picture:
            return obj.member_user.profile_picture.url

    @staticmethod
    def get_username(obj):
        return obj.username

    @staticmethod
    def get_email(obj):
        return obj.member_user.email

    @staticmethod
    def get_is_active(obj):
        return obj.member_user.is_active


class MemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField(
        error_messages={
            "required": "email is required",
            "blank": "email cannot be blank",
            "invalid": "enter a valid email",
        }
    )
    confirm_email = serializers.EmailField(
        error_messages={
            "required": "confirm_email is required",
            "blank": "confirm_email cannot be blank",
            "invalid": "enter a valid confirm_email",
        }
    )
    country = serializers.CharField(
        error_messages={"required": "country is required", "blank": "country cannot be blank"}
    )
    city_or_state = serializers.CharField(
        error_messages={
            "required": "city_or_state is required",
            "blank": "city_or_state cannot be blank",
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
        write_only=True,
        error_messages={
            "required": "confirm_password is required",
            "blank": "confirm_password cannot be blank",
        },
    )

    class Meta:
        model = Member
        fields = (
            "username",
            "email",
            "confirm_email",
            "country",
            "city_or_state",
            "password",
            "confirm_password",
        )

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        confirm_email = attrs.get("confirm_email")
        country = attrs.get("country")
        city_or_state = attrs.get("city_or_state")
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password")

        if not InputValidator(username).is_valid():
            raise serializers.ValidationError("username is required.")

        if not EmailValidator(email).is_valid():
            raise serializers.ValidationError("email is required.")

        if not EmailValidator(confirm_email).is_valid():
            raise serializers.ValidationError("confirm_email is required.")

        if email != confirm_email:
            raise serializers.ValidationError("email and confirm email does not match.")

        if not InputValidator(country).is_valid():
            raise serializers.ValidationError("country is required.")

        if not InputValidator(city_or_state).is_valid():
            raise serializers.ValidationError("city_or_state is required.")

        if not InputValidator(password).is_valid():
            raise serializers.ValidationError("password is required.")

        if not InputValidator(confirm_password).is_valid():
            raise serializers.ValidationError("confirm_password is required.")

        if password != confirm_password:
            raise serializers.ValidationError(
                "password and confirm password does not match."
            )

        if self.instance:
            users = (
                Member.objects.select_related("member_user")
                .all()
                .exclude(member_user=self.instance.member_user)
            )
        else:
            users = Member.objects.select_related("member_user").all()

        if users.filter(member_user__email=email).first():
            raise serializers.ValidationError("email already exists")

        if users.filter(username=username).first():
            raise serializers.ValidationError("username already exists")

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            country = validated_data.get("country")
            username = validated_data.get("username")
            email = validated_data.get("email")
            password = validated_data.get("password")
            city_or_state = validated_data.get("city_or_state")

            user = User.objects.create(email=email, password=password)
            member = Member.objects.create(
                member_user=user,
                name="Member",
                country=country,
                username=username,
                city_or_state=city_or_state,
            )

            EmailsHandler(to_user=user).set_welcome_email().send()
            return member
