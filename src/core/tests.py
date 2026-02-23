from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import Article, Publisher, User


class APIFeedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.reader = User.objects.create_user(
            username="reader1",
            password="pass12345",
            role=User.Role.READER,
        )
        self.journalist = User.objects.create_user(
            username="journ1",
            password="pass12345",
            role=User.Role.JOURNALIST,
        )
        self.editor = User.objects.create_user(
            username="editor1",
            password="pass12345",
            role=User.Role.EDITOR,
        )

        self.pub_a = Publisher.objects.create(name="Publisher A")
        self.pub_b = Publisher.objects.create(name="Publisher B")

        self.reader.subscribed_publishers.add(self.pub_a)
        self.reader.subscribed_journalists.add(self.journalist)

        self.url_feed = "/api/articles/feed/"
        self.url_publishers = "/api/articles/publishers/"
        self.url_journalists = "/api/articles/journalists/"

    def test_api_requires_authentication(self):
        response = self.client.get(self.url_feed)
        self.assertIn(response.status_code, (401, 403))

    def test_api_reader_only_blocks_journalist_and_editor(self):
        self.client.login(username="journ1", password="pass12345")
        response = self.client.get(self.url_feed)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username="editor1", password="pass12345")
        response = self.client.get(self.url_feed)
        self.assertEqual(response.status_code, 403)

    def test_publishers_endpoint_returns_only_approved_from_subscribed_publishers(self):
        Article.objects.create(
            title="Approved A",
            body="Body",
            publisher=self.pub_a,
            author=self.journalist,
            status=Article.Status.APPROVED,
        )
        Article.objects.create(
            title="Pending A",
            body="Body",
            publisher=self.pub_a,
            author=self.journalist,
            status=Article.Status.PENDING,
        )
        Article.objects.create(
            title="Approved B",
            body="Body",
            publisher=self.pub_b,
            author=self.journalist,
            status=Article.Status.APPROVED,
        )

        self.client.login(username="reader1", password="pass12345")
        response = self.client.get(self.url_publishers)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        titles = {item["title"] for item in data}
        self.assertEqual(titles, {"Approved A"})

    def test_journalists_endpoint_returns_only_approved_from_followed_journalists(self):
        other_journ = User.objects.create_user(
            username="journ2",
            password="pass12345",
            role=User.Role.JOURNALIST,
        )

        Article.objects.create(
            title="Followed Approved",
            body="Body",
            publisher=self.pub_b,
            author=self.journalist,
            status=Article.Status.APPROVED,
        )
        Article.objects.create(
            title="Followed Pending",
            body="Body",
            publisher=self.pub_b,
            author=self.journalist,
            status=Article.Status.PENDING,
        )
        Article.objects.create(
            title="Other Approved",
            body="Body",
            publisher=self.pub_b,
            author=other_journ,
            status=Article.Status.APPROVED,
        )

        self.client.login(username="reader1", password="pass12345")
        response = self.client.get(self.url_journalists)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        titles = {item["title"] for item in data}
        self.assertEqual(titles, {"Followed Approved"})

    def test_feed_endpoint_returns_union_without_duplicates(self):
        Article.objects.create(
            title="From Pub A",
            body="Body",
            publisher=self.pub_a,
            author=self.journalist,
            status=Article.Status.APPROVED,
        )
        Article.objects.create(
            title="From Followed Journalist",
            body="Body",
            publisher=self.pub_b,
            author=self.journalist,
            status=Article.Status.APPROVED,
        )
        Article.objects.create(
            title="Matches Both",
            body="Body",
            publisher=self.pub_a,
            author=self.journalist,
            status=Article.Status.APPROVED,
        )
        Article.objects.create(
            title="Pending Should Not Show",
            body="Body",
            publisher=self.pub_a,
            author=self.journalist,
            status=Article.Status.PENDING,
        )

        self.client.login(username="reader1", password="pass12345")
        response = self.client.get(self.url_feed)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        titles = [item["title"] for item in data]

        self.assertEqual(
            set(titles),
            {"From Pub A", "From Followed Journalist", "Matches Both"},
        )
        self.assertEqual(len(titles), 3)

        ids = [item["id"] for item in data]
        self.assertEqual(len(ids), len(set(ids)))


class XPostingTests(TestCase):
    def setUp(self):
        self.editor = User.objects.create_user(
            username="editor1",
            password="pass12345",
            role=User.Role.EDITOR,
        )
        self.journalist = User.objects.create_user(
            username="journ1",
            password="pass12345",
            role=User.Role.JOURNALIST,
        )
        self.publisher = Publisher.objects.create(name="Publisher A")

        self.article = Article.objects.create(
            title="Test Article",
            body="Body",
            publisher=self.publisher,
            author=self.journalist,
            status=Article.Status.PENDING,
        )

    @patch("core.services.x_client.requests.post")
    def test_post_to_x_attempted_on_approve_when_enabled(self, mock_post):
        mock_post.return_value.raise_for_status.return_value = None

        self.client.login(username="editor1", password="pass12345")

        with self.settings(
            X_POST_ENABLED=True,
            X_BEARER_TOKEN="fake-token",
            X_API_URL="https://api.x.com/2/tweets",
        ):
            url = reverse("core:decide_article", args=[self.article.pk])
            response = self.client.post(url, data={"action": "approve"})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(mock_post.called)