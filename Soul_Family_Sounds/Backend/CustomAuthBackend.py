from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from Utilities.Enums.RequestStatus import RequestStatus
from Utilities.Enums.UserTypes import UserType


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        user_model = get_user_model()
        usertype = kwargs.get("usertype")
        filter_args = {
            "email": email,
            "is_active": True,
            "is_deleted": False,
        }

        user = None

        try:
            if UserType.is_supplier(usertype):
                filter_args[
                    "supplier_details__request__status"
                ] = RequestStatus.COMPLETED.value
                user = (
                    user_model.objects.prefetch_related(
                        "supplier_details", "supplier_details__request"
                    )
                    .filter(**filter_args, usertype=UserType.SUPPLIER.value)
                    .first()
                )

            elif UserType.is_admin_or_staff(usertype):
                user = (
                    user_model.objects.prefetch_related("adminOrStaff_details")
                    .filter(**filter_args, usertype__in=UserType.get_admin_and_staff())
                    .first()
                )

            elif UserType.is_member(usertype):
                user = (
                    user_model.objects.prefetch_related("member_details")
                    .filter(**filter_args, usertype=UserType.MEMBER.value)
                    .first()
                )

            if user and user.check_password(password):
                return user

        except user_model.DoesNotExist:
            return None
