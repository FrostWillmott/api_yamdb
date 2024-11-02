from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

TEXT_OUTPUT_LIMIT = 20
MAX_LENGTH_TEXT = 50
LENGTH_INPUT_FIELD = 256
MAX_LENGTH_ROLE = 10
MAX_LENGTH_CONFIRMATION_CODE = 6
MAX_LENGTH_USERNAME = 150
MAX_LENGTH_NAME = 150
MAX_LENGTH_BIO = 500
MIN_SCORE = 1
MAX_SCORE = 10
VALIDATOR_MESSAGE = "Оценка должна быть от 1 до 10"


def me_username_validator(username):
    if username == "me":
        raise ValidationError("Username 'me' is not allowed.")


class User(AbstractUser):
    verbose_name = "Пользователь"
    verbose_name_plural = "Пользователи"
    ordering = ("username",)

    class Role(models.TextChoices):
        USER = "user", "User"
        MODERATOR = "moderator", "Moderator"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=MAX_LENGTH_ROLE,
        choices=Role.choices,
        default=Role.USER,
    )
    bio = models.TextField(blank=True, max_length=MAX_LENGTH_BIO)

    email = models.EmailField(
        unique=True,
    )
    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=(
            UnicodeUsernameValidator(
                message="Введите допустимое имя пользователя."
                "Это значение может содержать только буквы, "
                "цифры и символы @/./+/-/_",
            ),
            me_username_validator,
        ),
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        blank=True,
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        blank=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("-id",)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR

    def __str__(self):
        return self.username


class Genre(models.Model):
    name = models.CharField(
        max_length=LENGTH_INPUT_FIELD,
        verbose_name="Жанр",
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ("slug",)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        verbose_name="Категория",
        max_length=LENGTH_INPUT_FIELD,
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("slug",)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=LENGTH_INPUT_FIELD,
    )
    year = models.IntegerField(verbose_name="Год релиза")
    description = models.TextField(
        verbose_name="Описание",
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(Genre, verbose_name="Жанр", blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="titles",
        verbose_name="Категория",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name[:TEXT_OUTPUT_LIMIT]

    @property
    def rating(self):
        """Возвращает среднюю оценку произведения."""
        reviews = Review.objects.filter(title=self)
        return reviews.aggregate(Avg("score"))["score__avg"]

    @rating.setter
    def rating(self, value):
        self._rating = value


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
    )
    text = models.TextField("Текст отзыва")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор отзыва",
    )
    score = models.IntegerField(
        "Оценка произведения",
        validators=(
            MinValueValidator(
                MIN_SCORE,
                message=VALIDATOR_MESSAGE,
            ),
            MaxValueValidator(
                MAX_SCORE,
                message=VALIDATOR_MESSAGE,
            ),
        ),
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=["title", "author"],
                name="unique_review",
            ),
        ]

    def __str__(self):
        text = f"Отзыв на '{self.title}': {self.text}"
        return text[:MAX_LENGTH_TEXT]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзыв",
    )
    text = models.TextField("Текст комментария")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text[:MAX_LENGTH_TEXT]
