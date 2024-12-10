from django.db import transaction
from rest_framework import serializers

from Product_Management.models import PackSubmissions
from User_Management.models import AdminOrStaff, User
from Utilities.EmailsHandler import EmailsHandler
from Utilities.Enums import SubmissionStatus
from Utilities.Enums.UserTypes import UserType
from Utilities.Validators.EmailValidator import EmailValidator
from Utilities.Validators.InputValidator import InputValidator


class StaffsSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField("get_profile_picture")
    username = serializers.SerializerMethodField("get_username")
    email = serializers.SerializerMethodField("get_email")
    is_active = serializers.SerializerMethodField("get_is_active")

    class Meta:
        model = AdminOrStaff
        fields = ("profile_picture", "username", "email", "is_active", "name")

    @staticmethod
    def get_profile_picture(obj):
        if obj.admin_user.profile_picture:
            return obj.admin_user.profile_picture.url

    @staticmethod
    def get_username(obj):
        return obj.username

    @staticmethod
    def get_email(obj):
        return obj.admin_user.email

    @staticmethod
    def get_is_active(obj):
        return obj.admin_user.is_active


class StaffSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={"required": "name is required", "blank": "name cannot be blank"}
    )
    username = serializers.CharField(
        error_messages={
            "required": "username is required",
            "blank": "username cannot be blank",
        }
    )
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
        model = AdminOrStaff
        fields = (
            "username",
            "email",
            "confirm_email",
            "name",
            "password",
            "confirm_password",
        )

    def validate(self, attrs):
        name = attrs.get("name")
        email = attrs.get("email")
        username = attrs.get("username")
        password = attrs.get("password")
        confirm_email = attrs.get("confirm_email")
        confirm_password = attrs.pop("confirm_password")

        if not InputValidator(username).is_valid():
            raise serializers.ValidationError("username is required.")

        if not EmailValidator(email).is_valid():
            raise serializers.ValidationError("email is required.")

        if not EmailValidator(confirm_email).is_valid():
            raise serializers.ValidationError("confirm_email is required.")

        if email != confirm_email:
            raise serializers.ValidationError("email and confirm email does not match.")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

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
                AdminOrStaff.objects.select_related("admin_user")
                .all()
                .exclude(admin_user=self.instance.admin_user)
            )
        else:
            users = AdminOrStaff.objects.select_related("admin_user").all()

        if users.filter(admin_user__email=email).first():
            raise serializers.ValidationError("email already exists")

        if users.filter(username=username).first():
            raise serializers.ValidationError("username already exists")

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            name = validated_data.get("name")
            email = validated_data.get("email")
            username = validated_data.get("username")
            password = validated_data.get("password")

            user = User.objects.create(
                email=email, password=password, usertype=UserType.STAFF.value
            )
            admin = AdminOrStaff.objects.create(
                admin_user=user, name=name, username=username
            )

            submissions = PackSubmissions.objects.filter(approval_person__isnull=True).filter(
                status=SubmissionStatus.UPLOADED.value)

            for submission in submissions:
                submission.approval_person = user
                submission.save(update_fields=["approval_person"])

            EmailsHandler(to_user=user).set_welcome_email().send()
            return admin
