from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_staff
        )


class IsAnonymousUser(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsAuthenticatedUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "user"


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.role == "moderator"
        )

class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )