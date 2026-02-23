from rest_framework.permissions import BasePermission

from .models import User


class IsReader(BasePermission):
    message = "Only readers can access this endpoint."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.READER
        )