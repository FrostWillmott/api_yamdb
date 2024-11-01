from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


@admin.register(Title, Review, Comment, Category, Genre)
class ReviewAdmin(admin.ModelAdmin):
    pass
