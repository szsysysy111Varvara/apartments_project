from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, GroupViewSet
from .views import ListingViewSet, BookingViewSet, ReviewCreateView, ReviewListView, add_review
from . import views

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'bookings', BookingViewSet)
booking_detail = BookingViewSet.as_view({
    'post': 'cancel'
})

urlpatterns = [
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
    path('bookings/create/', BookingViewSet.as_view({'post': 'create_booking'}), name='booking-create'),
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:listing_id>/', ReviewListView.as_view(), name='review-list'),
    path('review/add/', add_review, name='add_review'),
]
