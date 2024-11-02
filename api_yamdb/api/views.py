from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (
    IsAdmin,
    IsAdminOrModeratorOrAuthorOrReadOnly,
    IsAdminOrReadOnly,
    IsUserOrReadOnly,
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
    UserProfileSerializer,
    UserSerializer,
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


class SignupViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = (IsUserOrReadOnly,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        email = serializer.validated_data["email"]
        user, _ = User.objects.get_or_create(username=username, email=email)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            "Ваш код подтверждения",
            f"Ваш код подтверждения: {confirmation_code}",
            "from@example.com",
            [user.email],
            fail_silently=False,
        )
        return Response(
            {"email": user.email, "username": user.username},
            status=status.HTTP_200_OK,
        )


class TokenViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(
                username=serializer.validated_data["username"],
            )
            if not default_token_generator.check_token(
                user, serializer.validated_data["confirmation_code"]
            ):
                return Response(
                    {"detail": "Неверный код подтверждения."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = "username"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["username"]
    search_fields = ["username"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        if User.objects.filter(email=email).exists():
            return Response(
                {"email": "Этот email уже зарегистрирован."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrModeratorOrAuthorOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete"]

    def _get_title(self):
        return get_object_or_404(Title, id=self.kwargs["title_id"])

    def get_queryset(self):
        title = self._get_title()
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title = self._get_title()
        user = self.request.user
        if user.is_anonymous:
            raise ValidationError(
                "Authentication credentials were not provided."
            )
        if Review.objects.filter(title=title, author=user).exists():
            raise ValidationError("You have already reviewed this title.")
        serializer.save(author=user, title=title)


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
