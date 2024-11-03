from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
    get_token,
    signup,
)

v1_router = DefaultRouter()

v1_router.register(r"users", UserViewSet, basename="user")
v1_router.register("titles", TitleViewSet, basename="titles")
v1_router.register("categories", CategoryViewSet, basename="categories")
v1_router.register("genres", GenreViewSet, basename="genres")

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
    path("auth/signup/", signup, name="signup"),
    path("auth/token/", get_token, name="get_token"),
    path("", include(v1_router.urls)),
]
