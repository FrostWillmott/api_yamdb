from django.contrib import admin

from .models import Comment, Review, Title


@admin.register(Title, Review, Comment)
class ReviewAdmin(admin.ModelAdmin):
    pass
