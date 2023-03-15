from rest_framework.permissions import BasePermission

class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        else:
            return request.user and request.user.is_authenticated