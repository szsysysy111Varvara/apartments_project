from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from users.models import Profile
from .models import Listing
from .serializers import ListingSerializer
from .permissions import IsRenter, IsLandlord

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'status']:
            return [permissions.IsAuthenticated(), IsLandlord(), IsOwnerOrReadOnly()]
        else:
            return [permissions.IsAuthenticated(), IsRenter()]


def perform_create(self, serializer):
    serializer.save(user=self.request.user)


@action(detail=True, methods=['put'])
def change_status(self, request, pk=None):
    listing = self.get_object()
    if listing.user != request.user:
        return Response({"error": "You do not have permission to change the status of this listing."},
                        status=status.HTTP_403_FORBIDDEN)
    new_status = 'inactive' if listing.status == 'active' else 'active'
    listing.status = new_status
    listing.save()
    return Response({"message": f"Listing {listing.id} status changed to {new_status}"}, status=status.HTTP_200_OK)


