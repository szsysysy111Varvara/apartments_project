from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsRenterOrReadOnly, IsLandlordOrReadOnly
from .decorators import landlord_required
from .filters import ListingFilter
from .models import Listing
from .permissions import IsRenter, IsLandlord
from .serializers import ListingSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']


    @action(detail=False, methods=['get'], permission_classes=[IsRenterOrReadOnly | IsLandlordOrReadOnly])
    def search(self, request):
        search_term = request.query_params.get('search', '')
        queryset = Listing.objects.filter(Q(title__icontains=search_term) | Q(description__icontains=search_term))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Listing.objects.all()
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        location = self.request.query_params.get('location')
        min_rooms = self.request.query_params.get('min_rooms')
        max_rooms = self.request.query_params.get('max_rooms')
        housing_type = self.request.query_params.get('housing_type')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if min_rooms:
            queryset = queryset.filter(rooms__gte=min_rooms)
        if max_rooms:
            queryset = queryset.filter(rooms__lte=max_rooms)
        if housing_type:
            queryset = queryset.filter(housing_type=housing_type)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'change_status']:
            return [IsAuthenticated(), IsLandlord(), IsOwnerOrReadOnly()]
        elif self.action == 'search':
            return [AllowAny()]
        else:
            return [IsAuthenticated(), IsRenter()]
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


