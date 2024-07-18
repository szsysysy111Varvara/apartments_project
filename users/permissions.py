from rest_framework import permissions


class IsRenterOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.profile.user_type == 'Renter':
                return True
        return request.method in permissions.SAFE_METHODS

class IsLandlordOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.profile.user_type == 'Landlord':
                return True
        return request.method in permissions.SAFE_METHODS