from rest_framework import serializers

from django.contrib.auth import get_user_model

from reviews.models import Category, Comment, Genre, Review, Title, User

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


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email"]
        extra_kwargs = {
            "username": {"validators": User.username.field.validators},
            "email": {"validators": User.email.field.validators},
        }

    def validate(self, attrs):
        if attrs.get("username").lower() == "me":
            raise serializers.ValidationError('Username "me" запрещен')
        if User.objects.filter(
            email=attrs["email"],
            username=attrs["username"],
        ).exists():
            return attrs

        validation_errors = {}
        if User.objects.filter(email=attrs["email"]).exists():
            validation_errors["email"] = "Пользователь с таким email уже существует"
        if User.objects.filter(username=attrs["username"]).exists():
            validation_errors["username"] = (
                "Пользователь с таким username уже существует"
            )
        if validation_errors:
            raise serializers.ValidationError(validation_errors)
        return attrs


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField()
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
