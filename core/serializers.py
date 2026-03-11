"""
Serializers for the News App REST API.

Serializers translate Django model instances into JSON-friendly Python data,
and validate/deserialize incoming API payloads when needed.
"""

from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for Article objects.

    Adds read-only convenience fields:
        - publisher_name: Article.publisher.name
        - author_username: Article.author.username
    """

    publisher_name = serializers.CharField(source="publisher.name", read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        """
        Serializer metadata.

        All fields are read-only because the API endpoints in this project
        are read/list-only feeds (writes occur via the web UI).
        """

        model = Article
        fields = [
            "id",
            "title",
            "body",
            "publisher",
            "publisher_name",
            "author",
            "author_username",
            "status",
            "created_at",
        ]
        read_only_fields = fields