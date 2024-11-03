from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.constants import (
    LENGTH_INPUT_FIELD,
    MAX_LENGTH_BIO,
    MAX_LENGTH_NAME,
    MAX_LENGTH_ROLE,
    MAX_LENGTH_TEXT,
    MAX_LENGTH_USERNAME,
    MAX_SCORE,
    MIN_SCORE,
    VALIDATOR_ERROR_MESSAGE,
)
from reviews.validators import forbidden_username_validator, validate_year


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "User"
        MODERATOR = "moderator", "Moderator"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        "Роль",
        max_length=MAX_LENGTH_ROLE,
        choices=Role.choices,
        default=Role.USER,
    )
    bio = models.TextField(
        "Биография",
        blank=True,
        max_length=MAX_LENGTH_BIO,
    )
    email = models.EmailField(
        unique=True,
    )
    username = models.CharField(
        "Имя пользователя",
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=(
            UnicodeUsernameValidator(),
            forbidden_username_validator,
        ),
    )
    first_name = models.CharField(
        "Имя",
        max_length=MAX_LENGTH_NAME,
        blank=True,
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=MAX_LENGTH_NAME,
        blank=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR


class Genre(models.Model):
    name = models.CharField(
        "Жанр",
        max_length=LENGTH_INPUT_FIELD,
    )
    slug = models.SlugField(
        "Слаг",
        unique=True,
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ("name",)

    def __str__(self):
        return f"Жанр: {self.name}"


class Category(models.Model):
    name = models.CharField(
        "Категория",
        max_length=LENGTH_INPUT_FIELD,
    )
    slug = models.SlugField(
        "Слаг",
        unique=True,
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self):
        return f"Категория: {self.name}"


class Title(models.Model):
    name = models.CharField(
        "Название",
        max_length=LENGTH_INPUT_FIELD,
    )
    year = models.SmallIntegerField(
        "Год релиза",
        validators=[validate_year],
    )
    description = models.TextField(
        "Описание",
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name="Жанр",
        blank=True,
    )
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
        ordering = ("name",)

    def __str__(self):
        return f"Произведение: {self.name}"


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
                message=VALIDATOR_ERROR_MESSAGE,
            ),
            MaxValueValidator(
                MAX_SCORE,
                message=VALIDATOR_ERROR_MESSAGE,
            ),
        ),
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("-pub_date",)
        constraints = [
            models.UniqueConstraint(
                fields=["title", "author"],
                name="unique_review",
            ),
        ]

    def __str__(self):
        return f"Обзор(id={self.id}, text={self.text[:MAX_LENGTH_TEXT]})"


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
        ordering = ("-pub_date",)

    def __str__(self):
        return f"Комментарий(id={self.id}, text={self.text[:MAX_LENGTH_TEXT]})"
