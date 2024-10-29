from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from reviews.models import Comment, Review, Title

from .serializers import CommentSerializer, ReviewSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
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


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)  # TODO add permissions

    def _get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def _get_review(self):
        title = self._get_title()
        return get_object_or_404(
            Review, id=self.kwargs['review_id'], title=title)

    def get_queryset(self):
        review = self._get_review()
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        review = self._get_review()
        user = self.request.user
        serializer.save(author=user, review=review)
