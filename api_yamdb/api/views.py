from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets, mixins
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Category, Genre, Title
from .serializers import (
    CategorySerializer,
    TitleSerializer,
    GenreSerializer,
)

class ListCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    #queryset = Title.objects.all()
    serializer_class = TitleSerializer


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer()

class CommentViewSet(viewsets.ModelViewSet):
    pass