from rest_framework.permissions import BasePermission


class IsMemberOfGroup(BasePermission):
    def has_permission(self, request, view):
        user_info = request.auth
        required_group = getattr(view, "required_group", None)
        if required_group and "groups" in user_info:
            return required_group in user_info["groups"]
        return False
