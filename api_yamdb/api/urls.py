
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    CommentViewSet,
    ReviewViewSet,
    SignupViewSet,
    TokenViewSet,
    UserProfileViewSet,
    UserViewSet,
    TitleViewSet,
    CategoryViewSet,
    GenreViewSet
)

v1_router = DefaultRouter()

v1_router.register("auth/signup", SignupViewSet, basename="signup")
v1_router.register("auth/token", TokenViewSet, basename="token")
v1_router.register(r"users", UserViewSet, basename="user")
v1_router.register(r"users/me", UserProfileViewSet, basename="user-profile")
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')

v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews",
    ReviewViewSet,
    basename="review",
)
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comment",
)

urlpatterns = [
    path(
        "v1/users/me/",
        UserProfileViewSet.as_view({"get": "retrieve", "patch": "update"}),
        name="user-profile",
    ),
    path("v1/", include(v1_router.urls)),
]
