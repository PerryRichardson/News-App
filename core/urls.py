from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    # Public
    path("", views.article_list, name="article_list"),
    path("articles/<int:pk>/", views.article_detail, name="article_detail"),

    # Publishers (Reader + Editor create)
    path("publishers/", views.publisher_list, name="publisher_list"),
    path("publishers/new/", views.create_publisher, name="create_publisher"),
    path(
        "publishers/<int:pk>/toggle/",
        views.toggle_publisher_subscription,
        name="toggle_publisher_subscription",
    ),

    # Journalists (Reader follow list)
    path("journalists/", views.journalist_list, name="journalist_list"),
    path(
        "journalists/<int:pk>/toggle/",
        views.toggle_journalist_follow,
        name="toggle_journalist_follow",
    ),

    # Journalist workflow
    path("journalist/", views.journalist_dashboard, name="journalist_dashboard"),
    path("journalist/new/", views.create_article, name="create_article"),

    # Editor workflow
    path("editor/", views.editor_queue, name="editor_queue"),
    path(
        "editor/articles/<int:pk>/decide/",
        views.decide_article,
        name="decide_article",
    ),

    # Account + subscriptions
    path("accounts/register/", views.register, name="register"),
    path("me/subscriptions/", views.my_subscriptions, name="my_subscriptions"),
]