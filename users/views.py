from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rentapp.decorators import landlord_required
from rentapp.forms_review import ReviewForm
from rentapp.models import Listing, Booking
from rentapp.serializers import BookingSerializer
from rentapp.views import IsOwnerOrReadOnly
from .models import Profile
from .serializers import UserRegistrationSerializer, GroupSerializer, UserSerializer, ProfileSerializer
from .permissions import IsLandlordOrReadOnly, IsRenterOrReadOnly


class UserRegistrationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]



class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        group = self.get_object()
        users = group.user_set.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)



    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsLandlordOrReadOnly()]
        else:
            return [permissions.IsAuthenticated(), IsRenterOrReadOnly()]




@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(request=request, username=user.username, password=password)

        if user is not None:
            login(request, user)
            return Response({"message": "User authenticated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['POST'])
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)

    return Response({"error": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


User = get_user_model()

class GroupListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

class GroupUserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        users = User.objects.filter(groups=group)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def profile_list(request):
    if request.method == 'GET':
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def profile_detail(request, pk):
    try:
        profile = Profile.objects.get(pk=pk)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@login_required
@landlord_required
@action(detail=True, methods=['patch'])
def partial_update(self, request, pk=None):
    listing = self.get_object()
    serializer = self.get_serializer(listing, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@login_required
@landlord_required
@action(detail=True, methods=['put'])
def update_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return HttpResponse("Listing updated successfully")

@login_required
@landlord_required
@action(detail=True, methods=['delete'])
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return HttpResponse("Listing deleted successfully")

@login_required
@landlord_required
@action(detail=True, methods=['put', 'patch'])
def toggle_listing_status(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return HttpResponse("Listing status toggled successfully")


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        if booking.listing.owner != request.user:
            return Response({"detail": "Not authorized to confirm this booking."}, status=status.HTTP_403_FORBIDDEN)
        booking.status = 'confirmed'
        booking.save()
        return Response({'status': 'Booking confirmed'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.user != request.user and booking.listing.owner != request.user:
            return Response({"detail": "Not authorized to cancel this booking."}, status=status.HTTP_403_FORBIDDEN)
        if timezone.now().date() > booking.start_date:
            return Response({"detail": "Cannot cancel past bookings."}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = 'cancelled'
        booking.save()
        return Response({'status': 'Booking cancelled'})


def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.owner = request.user
            review.save()
            return redirect('some_view')
    else:
        form = ReviewForm()
    return render(request, 'template.html', {'form': form})