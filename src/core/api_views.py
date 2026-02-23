from rest_framework.generics import ListAPIView

from .api_permissions import IsReader
from .models import Article
from .serializers import ArticleSerializer


class MyFeedArticlesAPIView(ListAPIView):
    """
    Returns APPROVED articles written by:
    - journalists the user follows OR
    - publishers the user subscribes to
    """
    serializer_class = ArticleSerializer
    permission_classes = [IsReader]

    def get_queryset(self):
        user = self.request.user

        qs = Article.objects.filter(status=Article.Status.APPROVED)

        qs = qs.filter(
            publisher__in=user.subscribed_publishers.all()
        ) | qs.filter(
            author__in=user.subscribed_journalists.all()
        )

        return qs.distinct().order_by("-created_at")


class MyPublisherArticlesAPIView(ListAPIView):
    """
    Returns APPROVED articles from publishers the user is subscribed to.
    """
    serializer_class = ArticleSerializer
    permission_classes = [IsReader]

    def get_queryset(self):
        user = self.request.user
        return (
            Article.objects.filter(
                status=Article.Status.APPROVED,
                publisher__in=user.subscribed_publishers.all(),
            )
            .order_by("-created_at")
        )


class MyJournalistArticlesAPIView(ListAPIView):
    """
    Returns APPROVED articles from journalists the user follows.
    """
    serializer_class = ArticleSerializer
    permission_classes = [IsReader]

    def get_queryset(self):
        user = self.request.user
        return (
            Article.objects.filter(
                status=Article.Status.APPROVED,
                author__in=user.subscribed_journalists.all(),
            )
            .order_by("-created_at")
        )