from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, GroupViewSet
from .views import ListingViewSet
from . import views

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('listings/', ListingViewSet.as_view({'post': 'create'}), name='listing-create'),
    path('listings/', ListingViewSet.as_view({'get': 'list'}), name='listing-list'),
    path('listings/<int:pk>/edit/', views.update_listing, name='update_listing'),
    path('listings/<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    path('listings/<int:pk>/toggle/', views.toggle_listing_status, name='toggle_listing_status'),
    path('listings/<int:pk>/partial_update/', views.partial_update, name='partial_update'),
]
