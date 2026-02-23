from django.urls import path

from .api_views import (
    MyFeedArticlesAPIView,
    MyJournalistArticlesAPIView,
    MyPublisherArticlesAPIView,
)

app_name = "core_api"

urlpatterns = [
    path("articles/feed/", MyFeedArticlesAPIView.as_view(), name="articles_feed"),
    path(
        "articles/publishers/",
        MyPublisherArticlesAPIView.as_view(),
        name="articles_publishers",
    ),
    path(
        "articles/journalists/",
        MyJournalistArticlesAPIView.as_view(),
        name="articles_journalists",
    ),
]