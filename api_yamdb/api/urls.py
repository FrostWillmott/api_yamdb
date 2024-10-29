from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import SignupViewSet, TokenViewSet, UserProfileViewSet, \
    UserViewSet

v1_router = DefaultRouter()
v1_router.register('auth/signup', SignupViewSet, basename='signup')
v1_router.register('auth/token', TokenViewSet, basename='token')
v1_router.register('users/me', UserProfileViewSet, basename='user-profile')
v1_router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]