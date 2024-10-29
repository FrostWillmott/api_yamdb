from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()

MAX_LENGTH_TEXT = 50


class Title(models.Model):
    pass


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
