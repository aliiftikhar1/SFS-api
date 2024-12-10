from Utilities.Enums.BaseEnum import BaseEnum


class UserType(BaseEnum):
    ADMIN = "Admin"
    STAFF = "Staff"
    MEMBER = "Member"
    SUPPLIER = "Supplier"

    @staticmethod
    def get_admin_and_staff():
        return [UserType.ADMIN.value, UserType.STAFF.value]

    @staticmethod
    def is_valid(usertype):
        return usertype in UserType.list()

    @staticmethod
    def is_admin_or_staff(usertype):
        return usertype in UserType.get_admin_and_staff()

    @staticmethod
    def is_admin_or_staff_or_member(usertype):
        return usertype in [
            UserType.ADMIN.value,
            UserType.STAFF.value,
            UserType.MEMBER.value,
        ]

    @staticmethod
    def is_admin_or_staff_or_supplier(usertype):
        return usertype in [
            UserType.ADMIN.value,
            UserType.STAFF.value,
            UserType.SUPPLIER.value,
        ]

    @staticmethod
    def is_member_or_supplier(usertype):
        return usertype in [UserType.MEMBER.value, UserType.SUPPLIER.value]

    @staticmethod
    def is_admin(usertype):
        return usertype == UserType.ADMIN.value

    @staticmethod
    def is_staff(usertype):
        return usertype == UserType.STAFF.value

    @staticmethod
    def is_supplier(usertype):
        return usertype == UserType.SUPPLIER.value

    @staticmethod
    def is_member(usertype):
        return usertype == UserType.MEMBER.value
