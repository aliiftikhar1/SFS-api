from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from User_Management.models import (
    User,
    Supplier,
    Artist,
    MusicContentInformation,
    Requests,
)
from Utilities.EmailsHandler import EmailsHandler
from Utilities.Enums.Boolean import Boolean
from Utilities.Enums.PrimaryDAW import PrimaryDAW
from Utilities.Enums.PrimaryTalents import PrimaryTalents
from Utilities.Enums.RequestStatus import RequestStatus
from Utilities.Enums.UserTypes import UserType
from Utilities.Validators.EmailValidator import EmailValidator
from Utilities.Validators.InputValidator import InputValidator


class SupplierApplySerializer(serializers.Serializer):
    first_name = serializers.CharField(
        error_messages={
            "required": "first_name is required",
            "blank": "first_name cannot be blank",
        }
    )
    last_name = serializers.CharField(
        error_messages={
            "required": "last_name is required",
            "blank": "last_name cannot be blank",
        }
    )
    profile_picture = serializers.ImageField(
        error_messages={
            "required": "profile_picture is required",
            "blank": "profile_picture cannot be blank",
        }
    )
    email = serializers.EmailField(
        error_messages={
            "required": "email is required",
            "blank": "email cannot be blank",
            "invalid": "enter a valid email",
        }
    )
    name = serializers.CharField(
        error_messages={"required": "name is required", "blank": "name cannot be blank"}
    )
    complete_residence_address = serializers.CharField(
        error_messages={
            "required": "complete_residence_address is" " required",
            "blank": "complete_residence_address cannot be blank",
        }
    )
    major_city = serializers.CharField(
        error_messages={
            "required": "major_city is required",
            "blank": "major_city cannot be blank",
        }
    )
    country_or_state = serializers.CharField(
        error_messages={
            "required": "country_or_state is required",
            "blank": "country_or_state cannot be blank",
        }
    )
    bio = serializers.CharField(
        min_length=100,
        max_length=1000,
        error_messages={"required": "bio is required", "blank": "bio cannot be blank"},
    )
    worked = serializers.BooleanField(
        error_messages={
            "required": "worked is required",
            "blank": "worked cannot be blank",
        }
    )
    released = serializers.BooleanField(
        error_messages={
            "required": "released is required",
            "blank": "released cannot be blank",
        }
    )
    talent = serializers.CharField(
        error_messages={
            "required": "talent is required",
            "blank": "talent cannot be blank",
        }
    )
    daw = serializers.CharField(
        error_messages={"required": "daw is required", "blank": "daw cannot be blank"}
    )

    class Meta:
        fields = (
            "first_name",
            "last_name",
            "profile_picture",
            "email",
            "name",
            "complete_residence_address",
            "major_city",
            "country_or_state",
            "bio",
            "worked",
            "released",
            "talent",
            "daw",
        )

    def validate(self, attrs):
        first_name = attrs.get("first_name")
        last_name = attrs.get("last_name")
        complete_residence_address = attrs.get("complete_residence_address")
        major_city = attrs.get("major_city")
        country_or_state = attrs.get("country_or_state")
        bio = attrs.get("bio")
        email = attrs.get("email")
        worked = attrs.get("worked")
        released = attrs.get("released")
        talent = attrs.get("talent")
        daw = attrs.get("daw")
        name = attrs.get("name")
        username = name.strip().lower().replace(" ", "_")

        if not EmailValidator(email).is_valid():
            raise serializers.ValidationError("email is required.")

        if not InputValidator(name).is_valid():
            raise serializers.ValidationError("name is required.")

        if not InputValidator(first_name).is_valid():
            raise serializers.ValidationError("first_name is required.")

        if not InputValidator(major_city).is_valid():
            raise serializers.ValidationError("major_city is required.")

        if not InputValidator(country_or_state).is_valid():
            raise serializers.ValidationError("country_or_state is required.")

        if not InputValidator(last_name).is_valid():
            raise serializers.ValidationError("last_name is required.")

        if not InputValidator(bio).is_valid():
            raise serializers.ValidationError("bio is required.")

        if len(bio.split(" ")) < 100:
            raise serializers.ValidationError("bio should have minimum of 100 words.")

        if not InputValidator(complete_residence_address).is_valid():
            raise serializers.ValidationError("complete_residence_address is required.")

        if self.instance:
            users = (
                Supplier.objects.select_related("supplier_user")
                .all()
                .exclude(supplier_user=self.instance.supplier_user)
            )
        else:
            users = Supplier.objects.select_related("supplier_user").all()

        if users.filter(supplier_user__email=email).first():
            raise serializers.ValidationError("supplier with this email already exists")

        if users.filter(Q(username__icontains=username)).first():
            raise serializers.ValidationError(
                "supplier with this artist name already exists"
            )

        if not InputValidator(worked).is_valid_option(Boolean.list()):
            raise serializers.ValidationError("worked should be a boolean.")

        if not InputValidator(released).is_valid_option(Boolean.list()):
            raise serializers.ValidationError("released should be a boolean.")

        if not InputValidator(talent).is_valid_option(PrimaryTalents.list()):
            raise serializers.ValidationError(f"'{talent}' is invalid talent.")

        if not InputValidator(daw).is_valid_option(PrimaryDAW.list()):
            raise serializers.ValidationError(f"'{daw}' is invalid daw.")

        attrs["username"] = username
        return attrs

    def create(self, validated_data):
        email = validated_data.get("email")
        name = validated_data.get("name")
        profile_picture = validated_data.get("profile_picture")
        username = validated_data.get("username")

        worked = validated_data.get("worked")
        released = validated_data.get("released")
        talent = validated_data.get("talent")
        daw = validated_data.get("daw")

        complete_residence_address = validated_data.get("complete_residence_address")
        major_city = validated_data.get("major_city")
        country_or_state = validated_data.get("country_or_state")
        bio = validated_data.get("bio")

        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")

        with transaction.atomic():
            supplier_user = User.objects.create(
                email=email,
                password=make_password(UserType.SUPPLIER.value),
                profile_picture=profile_picture,
                usertype=UserType.SUPPLIER.value,
                is_active=False,
                verified=True,
            )
        content_info = MusicContentInformation.objects.create(
            worked=worked, released=released, talent=talent, daw=daw
        )
        artist = Artist.objects.create(
            name=name,
            complete_residence_address=complete_residence_address,
            major_city=major_city,
            country_or_state=country_or_state,
            bio=bio,
            content_info=content_info,
        )
        supplier = Supplier.objects.create(
            supplier_user=supplier_user,
            first_name=first_name,
            last_name=last_name,
            contract=None,
            artist=artist,
            username=username,
        )
        requests = Requests.objects.create(supplier=supplier)
        EmailsHandler(supplier_user).set_supplier_request__email().send()
        return requests


class SupplierUploadContractSerializer(serializers.Serializer):
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
    password = serializers.CharField(
        error_messages={
            "required": "password is required",
            "blank": "password cannot be blank",
        }
    )
    confirm_password = serializers.CharField(
        error_messages={
            "required": "confirm_password is required",
            "blank": "confirm_password cannot be blank",
        }
    )
    contract = serializers.FileField(
        error_messages={
            "required": "contract is required",
            "blank": "contract cannot be blank",
        }
    )

    def validate(self, attrs):
        email = attrs.pop("email")
        username = attrs.pop("username")
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password")

        if not InputValidator(email).is_valid():
            raise serializers.ValidationError("email is required.")

        if not InputValidator(username).is_valid():
            raise serializers.ValidationError("username is required.")

        if not InputValidator(confirm_password).is_valid():
            raise serializers.ValidationError("confirm_password is required.")

        if not InputValidator(password).is_valid():
            raise serializers.ValidationError("password is required.")

        if password != confirm_password:
            raise serializers.ValidationError(
                "password and confirm password does not match"
            )

        instance = (
            Requests.objects.select_related("supplier", "supplier__supplier_user")
            .filter(
                supplier__supplier_user__email=email,
                supplier__username=username,
            )
            .first()
        )

        if instance is None:
            raise serializers.ValidationError("request not found")

        if instance.status not in [RequestStatus.APPROVED.value]:
            raise serializers.ValidationError("cannot sign contract")

        if instance.supplier.contract:
            raise serializers.ValidationError("supplier already has contract")

        attrs["instance"] = instance
        return attrs

    def create(self, validated_data):
        instance = validated_data.get("instance")
        contract = validated_data.get("contract")
        password = validated_data.get("password")

        instance.supplier.supplier_user.password = make_password(password)
        instance.supplier.supplier_user.save(update_fields=["password"])
        instance.supplier.contract = contract
        instance.supplier.save(update_fields=["contract"])

        if instance.status == RequestStatus.APPROVED.value:
            instance.status = RequestStatus.COMPLETED.value
            instance.save(update_fields=["supplier", "status"])

        instance.save(update_fields=["supplier"])

        return instance


class SupplierUpdateContractSerializer(serializers.Serializer):
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
    contract = serializers.FileField(
        error_messages={
            "required": "contract is required",
            "blank": "contract cannot be blank",
        }
    )

    def validate(self, attrs):
        email = attrs.pop("email")
        username = attrs.pop("username")

        if not InputValidator(email).is_valid():
            raise serializers.ValidationError("email is required.")

        if not InputValidator(username).is_valid():
            raise serializers.ValidationError("username is required.")

        instance = (
            Requests.objects.select_related("supplier", "supplier__supplier_user")
            .filter(
                supplier__supplier_user__email=email,
                supplier__username=username,
            )
            .first()
        )

        if instance is None:
            raise serializers.ValidationError("request not found")

        if instance.status not in [RequestStatus.APPROVED.value]:
            raise serializers.ValidationError("cannot sign contract")

        attrs["instance"] = instance
        return attrs

    def create(self, validated_data):
        instance = validated_data.get("instance")
        contract = validated_data.get("contract")

        instance.supplier.contract.delete(save=False)
        instance.supplier.contract = contract
        instance.supplier.save(update_fields=["contract"])

        if instance.status == RequestStatus.APPROVED.value:
            instance.status = RequestStatus.COMPLETED.value
            instance.save(update_fields=["supplier", "status"])

        instance.save(update_fields=["supplier"])

        return instance


class SupplierInterviewSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        error_messages={
            "required": "email is required",
            "blank": "email cannot be blank",
            "invalid": "enter a valid email",
        }
    )
    interview_date = serializers.DateField(
        error_messages={
            "required": "interview_date is required",
            "blank": "interview_date cannot be blank",
        }
    )

    class Meta:
        model = Requests
        fields = ("email", "interview_date")

    def validate(self, attrs):
        email = attrs.pop("email")

        if not InputValidator(email).is_valid():
            raise serializers.ValidationError("email is required.")

        instance = (
            Requests.objects.select_related("supplier", "supplier__supplier_user")
            .filter(supplier__supplier_user__email=email)
            .first()
        )

        if instance is None:
            raise serializers.ValidationError("request not found")

        if instance.status not in [
            RequestStatus.IN_PROCESS.value,
            RequestStatus.APPLIED.value,
        ]:
            raise serializers.ValidationError("request not in process")

        attrs["instance"] = instance
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            interview_date = validated_data.get("interview_date")

            instance = validated_data.get("instance")
            instance.interview_date = interview_date
            instance.status = RequestStatus.IN_PROCESS.value

            instance.save(update_fields=["interview_date", "status"])
            EmailsHandler(
                instance.supplier.supplier_user
            ).set_request_accepted_supplier_email(interview_date).send()
        return instance


class SupplierAccountsSerializer(serializers.ModelSerializer):
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
    password = serializers.CharField(
        error_messages={
            "required": "password is required",
            "blank": "password cannot be blank",
        }
    )
    confirm_password = serializers.CharField(
        error_messages={
            "required": "confirm_password is required",
            "blank": "confirm_password cannot be blank",
        }
    )

    class Meta:
        model = Requests
        fields = ("username", "email", "password", "confirm_password")

    def validate(self, attrs):
        email = attrs.pop("email")
        username = attrs.pop("username")

        if not EmailValidator().is_valid(email):
            raise serializers.ValidationError("email is required.")

        if not InputValidator(username).is_valid():
            raise serializers.ValidationError("username is required.")

        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password")

        if not InputValidator(password).is_valid():
            raise serializers.ValidationError("password is required.")

        if not InputValidator(confirm_password).is_valid():
            raise serializers.ValidationError("confirm_password is required.")

        if password != confirm_password:
            raise serializers.ValidationError(
                "password and confirm password does not match"
            )

        instance = (
            Requests.objects.select_related("supplier", "supplier__supplier_user")
            .filter(supplier__supplier_user__email=email, supplier__username=username)
            .first()
        )

        if instance is None:
            raise serializers.ValidationError("request not found")

        if instance.status not in [
            RequestStatus.PENDING.value,
            RequestStatus.COMPLETED.value,
        ]:
            raise serializers.ValidationError("request not approved yet")

        attrs["instance"] = instance
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            password = validated_data.get("password")

            instance = validated_data.get("instance")
            instance.supplier.supplier_user.password = make_password(password)
            instance.supplier.supplier_user.is_active = True
            instance.supplier.supplier_user.save(
                update_fields=["password", "is_active"]
            )

            if instance.status == RequestStatus.PENDING.value:
                instance.status = RequestStatus.COMPLETED.value
                instance.save(update_fields=["supplier", "status"])
            instance.save(update_fields=["supplier"])

            EmailsHandler(instance.supplier.supplier_user).set_new_supplier_email(
                password
            ).send()
        return instance


class SuppliersStatusSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField("get_full_name")
    country_or_state = serializers.SerializerMethodField("get_country_or_state")
    email = serializers.SerializerMethodField("get_email")

    class Meta:
        model = Requests
        fields = ("full_name", "country_or_state", "email")

    @staticmethod
    def get_full_name(obj):
        return f"{obj.supplier.first_name} {obj.supplier.last_name}"

    @staticmethod
    def get_country_or_state(obj):
        return obj.supplier.artist.country_or_state

    @staticmethod
    def get_email(obj):
        return obj.supplier.supplier_user.email


class SuppliersApprovedSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField("get_email")
    full_name = serializers.SerializerMethodField("get_full_name")
    username = serializers.SerializerMethodField("get_username")
    contract = serializers.SerializerMethodField("get_contract")
    profile_picture = serializers.SerializerMethodField("get_profile_picture")
    is_active = serializers.SerializerMethodField("get_is_active")

    class Meta:
        model = Requests
        fields = (
            "full_name",
            "username",
            "profile_picture",
            "contract",
            "email",
            "is_active",
        )

    @staticmethod
    def get_full_name(obj):
        return f"{obj.supplier.first_name} {obj.supplier.last_name}"

    @staticmethod
    def get_profile_picture(obj):
        if obj.supplier.supplier_user.profile_picture:
            return obj.supplier.supplier_user.profile_picture.url

    @staticmethod
    def get_email(obj):
        return obj.supplier.supplier_user.email

    @staticmethod
    def get_is_active(obj):
        return obj.supplier.supplier_user.is_active

    @staticmethod
    def get_contract(obj):
        if obj.supplier.contract:
            return obj.supplier.contract.url

    @staticmethod
    def get_username(obj):
        return obj.supplier.username


class SuppliersInProcessSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField("get_full_name")
    country_or_state = serializers.SerializerMethodField("get_country_or_state")
    email = serializers.SerializerMethodField("get_email")
    interview_date = serializers.SerializerMethodField("get_interview_date")

    class Meta:
        model = Requests
        fields = (
            "full_name",
            "country_or_state",
            "email",
            "interview_date",
        )

    @staticmethod
    def get_full_name(obj):
        return f"{obj.supplier.first_name} {obj.supplier.last_name}"

    @staticmethod
    def get_country_or_state(obj):
        return obj.supplier.artist.country_or_state

    @staticmethod
    def get_email(obj):
        return obj.supplier.supplier_user.email

    @staticmethod
    def get_interview_date(obj):
        return obj.interview_date


class SuppliersDetailsSerializer(serializers.ModelSerializer):
    supplier_name = serializers.SerializerMethodField("get_supplier_name")
    city = serializers.SerializerMethodField("get_city")
    country_or_state = serializers.SerializerMethodField("get_country_or_state")
    artist_name = serializers.SerializerMethodField("get_artist_name")
    profile_picture = serializers.SerializerMethodField("get_profile_picture")
    daw = serializers.SerializerMethodField("get_daw")
    talent = serializers.SerializerMethodField("get_talent")

    class Meta:
        model = Requests
        fields = (
            "supplier_name",
            "city",
            "artist_name",
            "daw",
            "country_or_state",
            "profile_picture",
            "talent",
        )

    @staticmethod
    def get_profile_picture(obj):
        if obj.supplier.supplier_user.profile_picture:
            return obj.supplier.supplier_user.profile_picture.url

    @staticmethod
    def get_supplier_name(obj):
        return f"{obj.supplier.first_name} {obj.supplier.last_name}"

    @staticmethod
    def get_artist_name(obj):
        return obj.supplier.artist.name

    @staticmethod
    def get_city(obj):
        return obj.supplier.artist.major_city

    @staticmethod
    def get_country_or_state(obj):
        return obj.supplier.artist.country_or_state

    @staticmethod
    def get_daw(obj):
        return obj.supplier.artist.content_info.daw

    @staticmethod
    def get_talent(obj):
        return obj.supplier.artist.content_info.talent
