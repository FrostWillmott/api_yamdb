from django.contrib.auth import get_user_model
from rest_framework import serializers
from reviews.models import Genre, Category, Title, Comment, Review

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
    rating = serializers.IntegerField(read_only=True)  # может поправить потом
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей произведений."""
    rating = serializers.IntegerField(required=False) # может поправить потом
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



class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    pub_date = serializers.DateTimeField(
        read_only=True,
        format="%Y-%m-%dT%H:%M:%SZ"
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    pub_date = serializers.DateTimeField(
        read_only=True,
        format="%Y-%m-%dT%H:%M:%SZ"
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')