from django.contrib.auth.base_user import BaseUserManager
from django.db import transaction

from Utilities.Enums.UserTypes import UserType


class UserManager(BaseUserManager):
    def create(
        self,
        email,
        password=None,
        verified=False,
        is_active=True,
        profile_picture=None,
        google_signup=False,
        usertype=UserType.MEMBER.value,
    ):
        """
        Creates and saves a User with the given email, password, and usertype.
        """
        if not email:
            raise ValueError("Users must have an email address")

        if not password:
            raise ValueError("Users must have a password")

        user = self.model(
            usertype=usertype,
            verified=verified,
            is_active=is_active,
            google_signup=google_signup,
            email=self.normalize_email(email),
            profile_picture=profile_picture,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs):
        with transaction.atomic():
            email = kwargs.pop("email")
            password = kwargs.pop("password")
            superuser = self.create(
                usertype=UserType.ADMIN.value,
                email=email,
                password=password,
                verified=True,
            )

            from User_Management.models import AdminOrStaff

            admin_or_staff_instance = AdminOrStaff.objects.create(
                admin_user=superuser, username="admin", name="Admin"
            )
            superuser.adminOrStaff_details = admin_or_staff_instance

            superuser.save()
            return superuser
