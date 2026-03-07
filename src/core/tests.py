"""
Test suite for the News App.

These tests focus on:
- Reader-only access control for DRF API endpoints
- Correct filtering logic for subscription feeds
- X posting hook is called on approval (mocked requests)
"""

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import Article, Publisher, User


def make_user(*, username: str, role: str, password: str = "pass1234"):
    """
    Create a user with a guaranteed-unique email for tests.
    """
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password=password,
        role=role,
    )


class APIFeedTests(TestCase):
    """
    Tests for the DRF subscription feed endpoints.

    Ensures that:
    - endpoints require authentication
    - endpoints are restricted to Reader users
    - endpoints return only APPROVED articles
    - feed endpoint returns a union without duplicates
    """

    def setUp(self):
        """
        Create baseline test data used by multiple tests.

        Returns:
            None
        """
        self.client = APIClient()

        self.reader = make_user(
            username="reader1",
            role=User.Role.READER,
            password="pass12345",
        )
        self.journalist = make_user(
            username="journ1",
            role=User.Role.JOURNALIST,
            password="pass12345",
        )
        self.editor = make_user(
            username="editor1",
            role=User.Role.EDITOR,
            password="pass12345",
        )

        self.pub_a = Publisher.objects.create(name="Publisher A")
        self.pub_b = Publisher.objects.create(name="Publisher B")

        self.reader.subscribed_publishers.add(self.pub_a)
        self.reader.subscribed_journalists.add(self.journalist)

        self.url_feed = "/api/articles/feed/"
        self.url_publishers = "/api/articles/publishers/"
        self.url_journalists = "/api/articles/journalists/"

    def test_api_requires_authentication(self):
        """
        Anonymous users should not be able to access the feed endpoint.

        Returns:
            None
        """
        response = self.client.get(self.url_feed)
        self.assertIn(response.status_code, (401, 403))

    def test_api_reader_only_blocks_journalist_and_editor(self):
        """
        Journalists and editors should be blocked from reader-only endpoints.

        Returns:
            None
        """
        self.client.login(username="journ1", password="pass12345")
        response = self.client.get(self.url_feed)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username="editor1", password="pass12345")
        response = self.client.get(self.url_feed)
        self.assertEqual(response.status_code, 403)

    def test_publishers_endpoint_returns_only_approved_from_subscribed_publishers(self):
        """
        Publisher subscription endpoint should return only APPROVED articles
        from publishers the reader is subscribed to.

        Returns:
            None
        """
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
        """
        Followed journalists endpoint should return only APPROVED articles
        authored by journalists the reader follows.

        Returns:
            None
        """
        other_journ = make_user(
            username="journ2",
            role=User.Role.JOURNALIST,
            password="pass12345",
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
        """
        Feed endpoint should return the union of:
        - articles from subscribed publishers
        - articles by followed journalists

        ...without duplicates, and only if APPROVED.

        Returns:
            None
        """
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
    """
    Tests for the optional X posting integration.

    Uses mocking to ensure that an HTTP request would be attempted when an
    editor approves an article and X posting is enabled.
    """

    def setUp(self):
        """
        Create baseline objects for X posting tests.

        Returns:
            None
        """
        self.editor = make_user(
            username="editor1",
            role=User.Role.EDITOR,
            password="pass12345",
        )
        self.journalist = make_user(
            username="journ1",
            role=User.Role.JOURNALIST,
            password="pass12345",
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
        """
        When X posting is enabled, approving an article should attempt a POST.

        Args:
            mock_post: Mocked requests.post function.

        Returns:
            None
        """
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