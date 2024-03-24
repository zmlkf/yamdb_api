from rest_framework import permissions


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(IsAdmin):

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            or request.method in permissions.SAFE_METHODS
        )


class IsAuthorOrModeratorsOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (IsAdminOrReadOnly().has_permission(request, view)
                or request.user.is_moderator
                or obj.author == request.user)
