"""
API permission classes for the News App.

These permissions are used by Django REST Framework (DRF) views to restrict
access based on authentication status and the user's role.
"""

from rest_framework.permissions import BasePermission

from .models import User


class IsReader(BasePermission):
    """
    Allow access only to authenticated users with the READER role.

    This is used to ensure that reader-facing API endpoints (e.g., subscription
    feeds) cannot be accessed by journalists, editors, or anonymous users.
    """

    message = "Only readers can access this endpoint."

    def has_permission(self, request, view):
        """
        Determine whether the incoming request has permission.

        Args:
            request: The incoming DRF request.
            view: The DRF view handling the request.

        Returns:
            bool: True if the user is authenticated and is a READER; otherwise False.
        """
        return request.user.is_authenticated and request.user.role == User.Role.READER