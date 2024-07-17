from rest_framework.permissions import BasePermission

class IsRenter(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'profile') and request.user.profile.user_type == 'Renter'

class IsLandlord(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'profile') and request.user.profile.user_type == 'Landlord'

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


