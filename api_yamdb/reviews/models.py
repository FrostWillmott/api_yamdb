from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

TEXT_OUTPUT_LIMIT = 20

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Жанр',)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        def __str__(self):
            return self.name


class Category(models.Model):
    name = models.CharField(verbose_name='Категория', max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        def __str__(self):
            return self.name


class Title(models.Model):
    name = models.CharField(verbose_name='Название', max_length=256)
    year = models.IntegerField(verbose_name='Год релиза')
    description = models.TextField(verbose_name='Описание',
                                   null=True, blank=True)
    genre = models.ManyToManyField(Genre, verbose_name='Жанр',
                                   blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                related_name='titles',
                                verbose_name='Категория',
                                null=True, blank=True)
    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        def __str__(self):
            return self.name[:TEXT_OUTPUT_LIMIT]


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews',
                              verbose_name='Произведение')
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews',
                               verbose_name='Автор отзыва')
    score = models.IntegerField('Оценка произведения',
                                validators=(
                                    MinValueValidator(1),
                                    MaxValueValidator(10)
                                ))
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Отзыв')
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

        def __str__(self):
            return self.text[:TEXT_OUTPUT_LIMIT]