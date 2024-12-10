from rest_framework import permissions

from User_Management.models import UserType


class AdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.usertype == UserType.ADMIN.value
