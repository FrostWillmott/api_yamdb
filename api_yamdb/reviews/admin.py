from django.contrib import admin

from .models import Review, Title


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass
