from rest_framework import mixins, viewsets
from api.permissions import IsAdminOrReadOnly
from rest_framework.filters import SearchFilter


class ListCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class SettingsCategoryGenreViewSet(ListCreateDestroyViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
