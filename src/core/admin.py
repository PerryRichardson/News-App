from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Article, Publisher, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Role & subscriptions",
            {
                "fields": (
                    "role",
                    "bio",
                    "subscribed_publishers",
                    "subscribed_journalists",
                )
            },
        ),
    )

    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "publisher", "author", "created_at")
    list_filter = ("status", "publisher")
    search_fields = ("title", "body")
