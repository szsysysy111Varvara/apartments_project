from rest_framework.permissions import BasePermission
from users.models import Profile

class IsRenter(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return Profile.objects.filter(user=request.user, user_type='Renter').exists()

class IsLandlord(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return Profile.objects.filter(user=request.user, user_type='Landlord').exists()

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

