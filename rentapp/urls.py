from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, GroupViewSet
from .views import ListingViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('listings/', ListingViewSet.as_view({'post': 'create'}), name='listing-create'),
    path('listings/', ListingViewSet.as_view({'get': 'list'}), name='listing-list'),
]
