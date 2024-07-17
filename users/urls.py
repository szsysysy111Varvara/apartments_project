from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import UserViewSet, GroupViewSet, user_login, user_logout, UserRegistrationAPIView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
]