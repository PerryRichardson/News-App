from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Article, Publisher, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Admin configuration for the custom User model.

    Extends Django's built-in UserAdmin to include:
    - role + bio
    - subscription relationships
    """

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

    # Show role/bio on the "Add user" page too (alongside default fields)
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (
            "Role",
            {
                "fields": (
                    "role",
                    "bio",
                )
            },
        ),
    )

    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")
    search_fields = ("username", "email")
    ordering = ("username",)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Admin configuration for Publisher."""

    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin configuration for Article."""

    list_display = ("title", "status", "publisher", "author", "created_at")
    list_filter = ("status", "publisher")
    search_fields = ("title", "body")
    ordering = ("-created_at",)