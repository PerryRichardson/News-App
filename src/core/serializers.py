from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    publisher_name = serializers.CharField(source="publisher.name", read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
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