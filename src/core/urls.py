from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.article_list, name="article_list"),
    path("articles/<int:pk>/", views.article_detail, name="article_detail"),
    path("publishers/", views.publisher_list, name="publisher_list"),
    path(
        "publishers/<int:pk>/toggle/",
        views.toggle_publisher_subscription,
        name="toggle_publisher_subscription",
    ),
    path("journalists/", views.journalist_list, name="journalist_list"),
    path(
        "journalists/<int:pk>/toggle/",
        views.toggle_journalist_follow,
        name="toggle_journalist_follow",
    ),
    path("journalist/", views.journalist_dashboard, name="journalist_dashboard"),
    path("journalist/new/", views.create_article, name="create_article"),
    path("editor/", views.editor_queue, name="editor_queue"),
    path("editor/articles/<int:pk>/decide/", views.decide_article, name="decide_article"),
    path("accounts/register/", views.register, name="register"),
    path("me/subscriptions/", views.my_subscriptions, name="my_subscriptions"),
]