from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg

from api.filters import TitleFilter
from api.permissions import (
    IsAdmin,
    IsAdminOrModeratorOrAuthorOrReadOnly,
    IsAdminOrReadOnly,
)
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserSerializer,
    UserSerializerAdmin,
)
from reviews.models import Category, Comment, Genre, Review, Title, User


class ListCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ("name",)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
    ]
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


@api_view(["POST"])
@permission_classes((AllowAny,))
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data["username"]
    email = serializer.validated_data["email"]
    user, _ = User.objects.get_or_create(username=username, email=email)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        "Ваш код подтверждения",
        f"Ваш код подтверждения: {confirmation_code}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    return Response(
        {"email": user.email, "username": user.username},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = get_object_or_404(
        User, username=serializer.validated_data["username"]
    )
    confirmation_code = serializer.validated_data["confirmation_code"]

    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            {"detail": "Неверный код подтверждения."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = AccessToken.for_user(user)
    return Response({"token": str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAdmin,)
    lookup_field = "username"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["username"]
    search_fields = ["username"]
    http_method_names = ["get", "post", "patch", "delete"]

    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.user.is_admin:
            return UserSerializerAdmin
        return UserSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrModeratorOrAuthorOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete"]

    def _get_title(self):
        return get_object_or_404(Title, id=self.kwargs["title_id"])

    def get_queryset(self):
        return self._get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self._get_title())


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrModeratorOrAuthorOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete"]

    def _get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs["review_id"],
            title__id=self.kwargs["title_id"],
        )

    def get_queryset(self):
        review = self._get_review()
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        review = self._get_review()
        user = self.request.user
        serializer.save(author=user, review=review)
