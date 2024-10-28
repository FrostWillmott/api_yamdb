from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Genre, Category, Title, Comment

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


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей произведений."""
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category')



class CommentsSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей комментариев."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment