"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rentapp.views import ListingViewSet, BookingViewSet, BookingCreateView, ReviewCreateView, ReviewListView, \
    add_review
from users import views
from users.views import UserRegistrationAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('rentapp/', include('rentapp.urls')),
    path('users/', include('users.urls')),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('profiles/', views.profile_list, name='profile-list'),
    path('profiles/<int:pk>/', views.profile_detail, name='profile-detail'),
    path('listings/', ListingViewSet.as_view({'post': 'create'}), name='listing-create'),
    path('listings/', ListingViewSet.as_view({'get': 'list'}), name='listing-list'),
    path('listings/<int:pk>/edit/', views.update_listing, name='update_listing'),
    path('listings/<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    path('listings/<int:pk>/toggle/', views.toggle_listing_status, name='toggle_listing_status'),
    path('listings/<int:pk>/partial_update/', views.partial_update, name='partial_update'),
    path('bookings/', BookingViewSet.as_view({'get': 'list_bookings'}), name='booking-list'),
    path('bookings/<int:pk>/cancel/', BookingViewSet.as_view({'post': 'cancel'}), name='booking-cancel'),
    path('bookings/<int:pk>/confirm/', BookingViewSet.as_view({'post': 'confirm'}), name='booking-confirm'),
    path('bookings/<int:pk>/reject/', BookingViewSet.as_view({'post': 'reject'}), name='booking-reject'),
    path('bookings/create/', BookingCreateView.as_view(), name='booking-create'),
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:listing_id>/', ReviewListView.as_view(), name='review-list'),
    path('review/add/', add_review, name='add_review'),
]
