
from django.contrib.auth import get_user_model
from rest_framework import serializers
from reviews.models import Genre, Category, Title, Comment, Review, User

User = get_user_model()


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей жанров."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для моделей категория."""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
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
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
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
        username = attrs.get("username")
        email = attrs.get("email")

        if username.lower() == "me":
            raise serializers.ValidationError('Username "me" запрещен')

        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            if existing_user.email == email:
                return attrs
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует"
            )

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email уже зарегистрирован")

        return attrs


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
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


class UserProfileSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ["role"]


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    pub_date = serializers.DateTimeField(
        read_only=True, format="%Y-%m-%dT%H:%M:%SZ"
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')



class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    pub_date = serializers.DateTimeField(
        read_only=True, format="%Y-%m-%dT%H:%M:%SZ"
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')