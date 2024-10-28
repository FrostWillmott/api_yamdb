from django.contrib.auth import get_user_model
from django.db import models

TEXT_OUTPUT_LIMIT = 20

User = get_user_model()


class Rewiew(models.Model):
    pass


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        def __str__(self):
            return self.name


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        def __str__(self):
            return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField()
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True)
    class Meta:
        def __str__(self):
            return self.name[:TEXT_OUTPUT_LIMIT]


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    rewiew = models.ForeignKey(
        Rewiew, on_delete=models.CASCADE, related_name='comments')   
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

