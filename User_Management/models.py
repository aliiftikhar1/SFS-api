from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from User_Management.Managers.UserManager import UserManager
from Utilities.Enums.PrimaryDAW import PrimaryDAW
from Utilities.Enums.PrimaryTalents import PrimaryTalents
from Utilities.Enums.RequestStatus import RequestStatus
from Utilities.Enums.UserTypes import UserType


class DateTimeModel(models.Model):
    """This Model adds created at and last modified fields to tables"""

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDelete(models.Model):
    """This Model adds deleted at and is deleted fields to tables"""

    deleted_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class User(AbstractBaseUser, DateTimeModel, SoftDelete):
    """This Model handles the basic details of Users"""

    email = models.EmailField(max_length=255, unique=True)

    auth_token = models.CharField(max_length=1000, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", max_length=1000, default=None, null=True, blank=True
    )

    google_signup = models.BooleanField(default=False)
    usertype = models.CharField(max_length=10, choices=UserType.choices)
    is_active = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    @property
    def is_staff(self):
        """Is the user a staff member?"""
        return self.usertype == UserType.STAFF.value

    @property
    def is_admin(self):
        """Is the user an admin?"""
        return self.usertype == UserType.ADMIN.value

    @property
    def is_supplier(self):
        """Is the user a supplier?"""
        return self.usertype == UserType.SUPPLIER.value

    @property
    def is_member(self):
        """Is the user a member?"""
        return self.usertype == UserType.MEMBER.value

    def get_user_details(self):
        if UserType.is_admin_or_staff(self.usertype):
            return (
                self.adminOrStaff_details
                if hasattr(self, "adminOrStaff_details")
                else None
            )

        elif UserType.is_supplier(self.usertype):
            return self.supplier_details if hasattr(self, "supplier_details") else None

        elif UserType.is_member(self.usertype):
            return self.member_details if hasattr(self, "member_details") else None


class AdminOrStaff(models.Model):
    admin_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="adminOrStaff_details",
    )
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)


class MusicContentInformation(models.Model):
    worked = models.BooleanField(default=False)
    released = models.BooleanField(default=False)
    talent = models.CharField(max_length=255, choices=PrimaryTalents.choices)
    daw = models.CharField(max_length=255, choices=PrimaryDAW.choices)

    def get_artist(self):
        if hasattr(self, "content_info_artist"):
            return self.content_info_artist


class Artist(models.Model):
    name = models.CharField(max_length=255)
    complete_residence_address = models.CharField(max_length=1000)
    major_city = models.CharField(max_length=255)
    country_or_state = models.CharField(max_length=255)
    bio = models.CharField(max_length=1000)
    content_info = models.ForeignKey(
        MusicContentInformation,
        on_delete=models.CASCADE,
        related_name="content_info_artist",
    )

    def get_supplier(self):
        if hasattr(self, "artist_supplier"):
            return self.artist_supplier


class Supplier(models.Model):
    supplier_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="supplier_details",
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contract = models.FileField(
        upload_to="contracts/", default=None, null=True, blank=True
    )
    username = models.CharField(max_length=255, unique=True)
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name="artist_supplier"
    )


class Requests(SoftDelete):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="request"
    )
    status = models.CharField(max_length=20, default=RequestStatus.APPLIED)
    hidden = models.BooleanField(default=False)
    interview_date = models.DateField(null=True, blank=True, default=None)


class Member(models.Model):
    member_user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="member_details"
    )
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    city_or_state = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
    username = models.CharField(max_length=255, unique=True)
