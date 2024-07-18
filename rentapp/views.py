import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from users.models import Profile
from .decorators import landlord_required
from .models import Listing
from .serializers import ListingSerializer
from .permissions import IsRenter, IsLandlord
from django.http import HttpResponse, HttpResponseForbidden


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'change_status', 'partial_update']:
            return [permissions.IsAuthenticated(), IsLandlord(), IsOwnerOrReadOnly()]
        else:
            return [permissions.IsAuthenticated(), IsRenter()]

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
@action(detail=True, methods=['patch'])
def partial_update(self, request, pk=None):
    listing = self.get_object()
    serializer = self.get_serializer(listing, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
@login_required
@landlord_required
def update_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return HttpResponse("Listing updated successfully")

@login_required
@landlord_required
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return HttpResponse("Listing deleted successfully")

@login_required
@landlord_required
def toggle_listing_status(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return HttpResponse("Listing status toggled successfully")


