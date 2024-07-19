from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.permissions import IsRenterOrReadOnly, IsLandlordOrReadOnly
from . import serializers
from .decorators import landlord_required
from .filters import ListingFilter
from .models import Listing, Booking
from .permissions import IsRenter, IsLandlord
from .serializers import ListingSerializer, BookingSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .permissions import IsBookingOwner, IsBookingRenter
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


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookingOwner]

    def get_permissions(self):
        if self.action in ['confirm', 'cancel', 'reject']:
            return [IsAuthenticated(), IsLandlord()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    @action(detail=False, methods=['post'])
    def create_booking(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            listing = serializer.validated_data['listing']
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            existing_bookings = Booking.objects.filter(listing=listing,
                                                       start_date__lt=end_date,
                                                       end_date__gt=start_date)
            if existing_bookings.exists():
                return Response({'detail': 'This listing is already booked for the selected dates.'},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=['get'])
    def list_bookings(self, request):
        user = request.user

        if user.profile.user_type == 'Landlord':
            queryset = Booking.objects.filter(listing__owner=user)
        else:
            queryset = Booking.objects.filter(user=user)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        try:
            booking = self.get_object()
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        if booking.owner != request.user:
            return Response({"detail": "You do not have permission to cancel this booking."},
                            status=status.HTTP_403_FORBIDDEN)

        if booking.start_date <= timezone.now() + timedelta(days=1):
            return Response({"detail": "You can only cancel bookings at least one day before the start date."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Logic to cancel the booking
        booking.status = 'cancelled'
        booking.save()

        return Response({"detail": "Booking cancelled successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        booking = self.get_object()

        if booking.listing.owner != request.user:
            return Response({'detail': 'Only the owner of the listing can confirm this booking.'},
                            status=status.HTTP_403_FORBIDDEN)

        if booking.status != 'Pending':
            return Response({'detail': 'Booking is not in a pending state.'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'Confirmed'
        booking.save()

        return Response({'status': 'Booking confirmed'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        booking = self.get_object()

        if booking.listing.owner != request.user:
            return Response({'detail': 'Only the owner of the listing can reject this booking.'},
                            status=status.HTTP_403_FORBIDDEN)

        if booking.status != 'Pending':
            return Response({'detail': 'Booking is not in a pending state.'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'Rejected'
        booking.save()

        return Response({'status': 'Booking rejected'}, status=status.HTTP_200_OK)


class BookingCreateView(CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        listing_id = self.request.data.get('listing')
        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Listing does not exist.")

        serializer.save(owner=self.request.user)

class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(owner=user)