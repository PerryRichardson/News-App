"""
Database models for the News App.

This module defines the core data structures used by the application:
- Publisher: organizations that publish articles
- User: custom user model with a role (Reader, Journalist, Editor) and subscription relations
- Article: news article workflow with PENDING/APPROVED/REJECTED states
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Publisher(models.Model):
    """
    A publisher that can have articles associated with it.

    Attributes:
        name (str): Human-readable publisher name.
        description (str): Optional description/bio for the publisher.
    """

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        """
        Return a human-readable string representation.

        Returns:
            str: The publisher's name.
        """
        return self.name


class User(AbstractUser):
    """
    Custom user model with roles and subscription relationships.

    Roles:
        - READER: can subscribe to publishers/journalists and access reader API feeds
        - JOURNALIST: can submit articles (PENDING)
        - EDITOR: can approve/reject articles

    Attributes:
        role (str): One of the Role choices.
        bio (str): Optional user bio.
        subscribed_publishers (ManyToMany[Publisher]): Publishers this user subscribes to.
        subscribed_journalists (ManyToMany[User]): Journalists this user follows.
    """

    class Role(models.TextChoices):
        """Enumerated roles used for permission checks and UI display."""

        READER = "READER", "Reader"
        JOURNALIST = "JOURNALIST", "Journalist"
        EDITOR = "EDITOR", "Editor"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.READER,
    )

    bio = models.TextField(blank=True)
    email = models.EmailField(unique=True)

    subscribed_publishers = models.ManyToManyField(
        Publisher,
        related_name="subscribers",
        blank=True,
    )

    subscribed_journalists = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,
    )

    def __str__(self) -> str:
        """
        Return a human-readable string representation.

        Returns:
            str: The user's username.
        """
        return self.username


class Article(models.Model):
    """
    A news article with an editorial workflow.

    Status flow:
        PENDING -> APPROVED or REJECTED

    Attributes:
        title (str): Article title.
        body (str): Article body text.
        publisher (Publisher): The publisher associated with the article.
        author (User): The journalist who wrote the article.
        status (str): One of Status choices.
        decision_reason (str): Optional reason provided when rejecting.
        decided_at (datetime): Timestamp when approved/rejected.
        created_at (datetime): Created timestamp.
        updated_at (datetime): Updated timestamp.
    """

    class Status(models.TextChoices):
        """Enumerated status values for article moderation."""

        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    title = models.CharField(max_length=200)
    body = models.TextField()

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="articles",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="articles",
        limit_choices_to={"role": User.Role.JOURNALIST},
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    decision_reason = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def approve(self) -> None:
        """
        Mark the article as approved and set the decision timestamp.

        Returns:
            None
        """
        self.status = self.Status.APPROVED
        self.decided_at = timezone.now()
        self.save(update_fields=["status", "decided_at", "updated_at"])

    def reject(self, reason: str = "") -> None:
        """
        Mark the article as rejected and store a rejection reason.

        Args:
            reason (str): Optional editorial reason for the rejection.

        Returns:
            None
        """
        self.status = self.Status.REJECTED
        self.decision_reason = reason
        self.decided_at = timezone.now()
        self.save(update_fields=["status", "decision_reason", "decided_at", "updated_at"])

    def __str__(self) -> str:
        """
        Return a human-readable string representation.

        Returns:
            str: The article title.
        """
        return self.title