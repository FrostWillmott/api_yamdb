from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, RegexValidator
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg


class NotMeValidator(RegexValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(r"^(?!me$).*", *args, **kwargs)


class User(AbstractUser):
    ROLE_CHOICES = [
        ("user", "User"),
        ("moderator", "Moderator"),
        ("admin", "Admin"),
    ]
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default="user"
    )
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    email = models.EmailField(
        max_length=254,
        validators=[MaxLengthValidator(254), NotMeValidator()],
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            MaxLengthValidator(150),
            RegexValidator(
                regex=r"^[\w.@+-]+\Z",
                message=r"Username must match the pattern: ^[\w.@+-]+\Z",
            ),
        ],
    )
    first_name = models.CharField(
        max_length=150,
        validators=[MaxLengthValidator(150)],
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        validators=[MaxLengthValidator(150)],
        blank=True,
    )

    @property
    def is_admin(self):
        return self.role == "admin" or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == "moderator"
User = get_user_model()

MAX_LENGTH_TEXT = 50


class Title(models.Model):

    @property
    def rating(self):
        '''Возвращает среднюю оценку произведения.'''
        return self.reviews.aggregate(Avg('score'))['score__avg']


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

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review',
            )
        ]

    def __str__(self):
        return self.text[:MAX_LENGTH_TEXT]


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Отзыв')
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self):
        return self.text[:MAX_LENGTH_TEXT]

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
