from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Publisher(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        READER = "READER", "Reader"
        JOURNALIST = "JOURNALIST", "Journalist"
        EDITOR = "EDITOR", "Editor"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.READER,
    )

    bio = models.TextField(blank=True)

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
        return self.username


class Article(models.Model):
    class Status(models.TextChoices):
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
        self.status = self.Status.APPROVED
        self.decided_at = timezone.now()
        self.save(update_fields=["status", "decided_at", "updated_at"])

    def reject(self, reason: str = "") -> None:
        self.status = self.Status.REJECTED
        self.decision_reason = reason
        self.decided_at = timezone.now()
        self.save(update_fields=["status", "decision_reason", "decided_at", "updated_at"])

    def __str__(self) -> str:
        return self.title
