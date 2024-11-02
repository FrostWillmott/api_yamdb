from rest_framework.routers import DefaultRouter

from django.urls import include, path

from api.views import (
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
<<<<<<< HEAD
v1_router.register("titles", TitleViewSet, basename="titles")
v1_router.register("categories", CategoryViewSet, basename="categories")
v1_router.register("genres", GenreViewSet, basename="genres")
=======
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
>>>>>>> 52b05a1fd46d73e0bb6e69af0a283ff1c6ed83dd

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
    path("v1/auth/signup/", signup, name="signup"),
    path("v1/auth/token/", get_token, name="get_token"),
    path("v1/", include(v1_router.urls)),
]
