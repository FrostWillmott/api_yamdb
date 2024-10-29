from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from reviews.models import Review, Title

from .serializers import ReviewSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)  # TODO add permissions

    def _get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        title = self._get_title()
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title = self._get_title()
        user = self.request.user
        serializer.save(author=user, title=title)
