from rest_framework import permissions

from User_Management.models import UserType


class SupplierPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.usertype == UserType.SUPPLIER.value
