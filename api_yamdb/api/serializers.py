from rest_framework import serializers

from django.contrib.auth import get_user_model
<<<<<<< HEAD
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
=======
from rest_framework import serializers
from reviews.models import Genre, Category, Title, Comment, Review, User
>>>>>>> 52b05a1fd46d73e0bb6e69af0a283ff1c6ed83dd

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
<<<<<<< HEAD
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

=======
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'genre', 'category', 'description', 'rating')


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей произведений."""
>>>>>>> 52b05a1fd46d73e0bb6e69af0a283ff1c6ed83dd
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
<<<<<<< HEAD
        fields = ("id", "name", "year", "genre", "category", "description")


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=[UnicodeUsernameValidator(), me_username_validator]
    )
    email = serializers.EmailField(max_length=254)

    def validate(self, attrs):
        user_by_email = User.objects.filter(email=attrs["email"]).first()
        user_by_username = User.objects.filter(
            username=attrs["username"]
        ).first()

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
=======
        fields = ('id', 'name', 'year', 'genre', 'category', 'description')

class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email"]
        extra_kwargs = {
            "username": {"validators": User.username.field.validators},
            "email": {"validators": User.email.field.validators},
        }

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        return user

    def validate(self, attrs):
        if attrs.get("username").lower() == "me":
            raise serializers.ValidationError('Username "me" запрещен')
        if User.objects.filter(email=attrs["email"],
                               username=attrs["username"]).exists():
            return attrs
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует")
>>>>>>> 52b05a1fd46d73e0bb6e69af0a283ff1c6ed83dd
        return attrs


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(max_length=MAX_LENGTH_USERNAME,
        validators=[UnicodeUsernameValidator(), me_username_validator])
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей User."""

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        ]


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