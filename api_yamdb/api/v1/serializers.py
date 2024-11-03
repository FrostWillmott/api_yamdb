from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

from reviews.models import (
    MAX_LENGTH_USERNAME,
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User,
)
from reviews.validators import forbidden_username_validator

User = get_user_model()


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей жанров."""

    class Meta:
        model = Genre
        fields = ("name", "slug")


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для моделей категория."""

    class Meta:
        model = Category
        fields = ("name", "slug")


class TitleBaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для модели Title."""

    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "genre",
            "category",
            "description",
            "rating",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["description"] = representation.get("description") or ""
        representation["category"] = CategorySerializer(
            instance.category,
        ).data or {"name": "", "slug": ""}
        representation["genre"] = (
            GenreSerializer(
                instance.genre.all(),
                many=True,
            ).data
            or []
        )
        return representation


class TitleReadSerializer(TitleBaseSerializer):
    """Сериализатор для чтения данных модели Title."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()


class TitleWriteSerializer(TitleBaseSerializer):
    """Сериализатор для записи данных модели Title."""

    genre = serializers.SlugRelatedField(
        slug_field="slug",
        many=True,
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
    )

    # def validate_year(self, value):
    #     if value > datetime.now().year:
    #         raise serializers.ValidationError(
    #             "Год выпуска не может быть больше текущего",
    #         )
    #     return value

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо указать жанр")
        return value


class SignupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=(UnicodeUsernameValidator(), forbidden_username_validator),
    )
    email = serializers.EmailField(max_length=254)

    def validate(self, attrs):
        user_by_email = User.objects.filter(email=attrs["email"]).first()
        user_by_username = User.objects.filter(
            username=attrs["username"],
        ).first()

        if user_by_email == user_by_username:
            return attrs
        error_msg = {}
        if user_by_email is not None:
            error_msg["email"] = "Пользователь с таким email существует"
        if user_by_username is not None:
            error_msg["username"] = "Пользователь с таким username существует"
        raise serializers.ValidationError(error_msg)


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=(UnicodeUsernameValidator(), forbidden_username_validator),
    )
    confirmation_code = serializers.CharField()


class UserSerializerAdmin(serializers.ModelSerializer):
    """Сериализатор для моделей User с правом менять роли."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class UserSerializer(UserSerializerAdmin):
    """Сериализатор для моделей User без прав менять роли."""

    class Meta(UserSerializerAdmin.Meta):
        read_only_fields = ("role",)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей Review."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    # pub_date = serializers.DateTimeField(
    #     read_only=True,
    #     format="%Y-%m-%dT%H:%M:%SZ",
    # )

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")

    def validate(self, attrs):
        if self.context["request"].method == "POST":
            if self.Meta.model.objects.filter(
                author=self.context["request"].user,
                title=self.context["view"].kwargs["title_id"],
            ).exists():
                raise serializers.ValidationError("Отзыв уже существует")
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей Comment."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    # pub_date = serializers.DateTimeField(
    #     read_only=True,
    #     format="%Y-%m-%dT%H:%M:%SZ",
    # )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
