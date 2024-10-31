from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and (
            request.user.is_admin or request.user.is_staff))

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin))

class IsModeratorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS or(request.user.is_authenticated and request.user.role == "moderator"))

class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )