import random
import string

from api.permissions import IsAdmin, IsAuthenticatedOrReadOnly, \
    IsAdminOrReadOnly, IsAdminOrModeratorOrAuthorOrReadOnly
from api.serializers import (
    SignupSerializer,
    TokenSerializer,
    UserProfileSerializer,
    UserSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    CommentSerializer,
    ReviewSerializer
)
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Comment, Review, Title, User, Category, Genre

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
    filter_backends = (filters.SearchFilter,)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer


class CategoryViewSet(SettingsCategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(SettingsCategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class SignupViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        confirmation_code = self._generate_confirmation_code()
        user.confirmation_code = confirmation_code
        user.save()

        self._send_confirmation_email(user, confirmation_code)

        return Response(
            {"email": user.email, "username": user.username},
            status=status.HTTP_200_OK,
        )

    def _generate_confirmation_code(self):
        """Генерирует случайный код подтверждения."""
        return "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )

    def _send_confirmation_email(self, user, confirmation_code):
        """Отправляет код подтверждения на email пользователя."""
        send_mail(
            subject="Ваш код подтверждения",
            message=f"Ваш код подтверждения: {confirmation_code}",
            from_email="from@example.com",
            recipient_list=[user.email],
            fail_silently=False,
        )


class TokenViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(
                username=serializer.validated_data["username"],
            )
            if (
                user.confirmation_code
                != serializer.validated_data["confirmation_code"]
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

        refresh = RefreshToken.for_user(user)
        return Response(
            {"token": str(refresh.access_token)}, status=status.HTTP_200_OK
        )


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
            instance, data=request.data, partial=partial
        )
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
    http_method_names = ["get", "post", "patch", "delete"]

    @action(detail=False, methods=["get", "patch"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        if request.method == "PATCH":
            if request.data.get("role"):
                return Response(
                    {"role": "Вы не можете менять роль пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrModeratorOrAuthorOrReadOnly)

    def _get_title(self):
        return get_object_or_404(Title, id=self.kwargs["title_id"])

    def get_queryset(self):
        title = self._get_title()
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title = self._get_title()
        user = self.request.user
        serializer.save(author=user, title=title)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrModeratorOrAuthorOrReadOnly)

    def _get_title(self):
        return get_object_or_404(Title, id=self.kwargs["title_id"])

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