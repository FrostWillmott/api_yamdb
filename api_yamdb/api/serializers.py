from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator

from reviews.models import (
    MAX_LENGTH_USERNAME,
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User,
    me_username_validator,
)

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


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных модели Title."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()

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


class TitleWriteSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Title
        fields = ("id", "name", "year", "genre", "category", "description")


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=[UnicodeUsernameValidator(), me_username_validator],
    )
    email = serializers.EmailField(max_length=254)

    def validate(self, attrs):
        user_by_email = User.objects.filter(email=attrs["email"]).first()
        user_by_username = User.objects.filter(username=attrs["username"]).first()

        if user_by_email != user_by_username:
            error_msg = {}
            if user_by_email is not None:
                error_msg["email"] = (
                    "Пользователь с таким email уже существует"
                )
            if user_by_username is not None:
                error_msg["username"] = (
                    "Пользователь с таким username уже существует"
                )
            raise serializers.ValidationError(error_msg)
        return attrs


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(max_length=MAX_LENGTH_USERNAME,
        validators=[UnicodeUsernameValidator(), me_username_validator])
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
    pub_date = serializers.DateTimeField(
        read_only=True,
        format="%Y-%m-%dT%H:%M:%SZ",
    )

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
    pub_date = serializers.DateTimeField(
        read_only=True,
        format="%Y-%m-%dT%H:%M:%SZ",
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
