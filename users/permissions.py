from rest_framework import permissions
#from rest_framework.permissions import BasePermission

class IsRenterOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.profile.user_type == 'Renter':
                return True
            return False
        return False

class IsLandlordOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.profile.user_type == 'Landlord':
                return True
            return False
        return False