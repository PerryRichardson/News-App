"""
Views for the News App.

This module contains Django view functions for:
- reader browsing (home, article detail)
- subscriptions (publishers, journalists, my subscriptions)
- journalist workflows (dashboard, create article)
- editor workflows (review queue, approve/reject)
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ArticleForm, PublisherForm, RegistrationForm
from .models import Article, Publisher, User
from .services.x_client import post_article_to_x


def register(request):
    """
    Register a new user account.

   Behavior:
    - Creates a user account and assigns a role based on the registration form.
    - Role selection is limited to Reader/Journalist to prevent privilege escalation.

    Args:
        request: Django HttpRequest.

    Returns:
        HttpResponse: Rendered registration form or redirect on success.
    """
    if request.user.is_authenticated:
        return redirect("core:article_list")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("core:article_list")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def article_list(request):
    """
    Display the public homepage article list (APPROVED only).

    Args:
        request: Django HttpRequest.

    Returns:
        HttpResponse: Rendered article list.
    """
    articles = Article.objects.filter(status=Article.Status.APPROVED).order_by(
        "-created_at"
    )
    return render(request, "core/article_list.html", {"articles": articles})


def article_detail(request, pk: int):
    """
    Display a single approved article by primary key.

    Args:
        request: Django HttpRequest.
        pk (int): Article primary key.

    Returns:
        HttpResponse: Rendered article detail page.
    """
    article = get_object_or_404(Article, pk=pk, status=Article.Status.APPROVED)
    return render(request, "core/article_detail.html", {"article": article})

@login_required
def create_publisher(request):
    """
    Editor-only view to create publishers that journalists can publish under.

    Args:
        request: Django HttpRequest.

    Returns:
        HttpResponse: Rendered create publisher form or redirect on success.

    Raises:
        HttpResponseForbidden: If user is not an editor.
    """
    if request.user.role != User.Role.EDITOR:
        return HttpResponseForbidden("Only editors can create publishers.")

    if request.method == "POST":
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Publisher created.")
            return redirect("core:publisher_list")
    else:
        form = PublisherForm()

    return render(request, "core/create_publisher.html", {"form": form})

@login_required
def publisher_list(request):
    """
    List all publishers and show which ones the current user is subscribed to.

    Args:
        request: Django HttpRequest.

    Returns:
        HttpResponse: Rendered publisher list page.
    """
    publishers = Publisher.objects.order_by("name")
    subscribed_ids = set(request.user.subscribed_publishers.values_list("id", flat=True))
    context = {"publishers": publishers, "subscribed_ids": subscribed_ids}
    return render(request, "core/publisher_list.html", context)


@login_required
def toggle_publisher_subscription(request, pk: int):
    """
    Subscribe/unsubscribe the current user to a publisher.

    Expects POST. Non-POST requests are redirected back to publisher list.

    Args:
        request: Django HttpRequest.
        pk (int): Publisher primary key.

    Returns:
        HttpResponseRedirect: Redirect back to publisher list.
    """
    if request.method != "POST":
        return redirect("core:publisher_list")

    publisher = get_object_or_404(Publisher, pk=pk)

    if request.user.subscribed_publishers.filter(pk=publisher.pk).exists():
        request.user.subscribed_publishers.remove(publisher)
    else:
        request.user.subscribed_publishers.add(publisher)

    return redirect("core:publisher_list")


@login_required
def journalist_list(request):
    """
    List all journalists and show which ones the current user follows.

    Args:
        request: Django HttpRequest.

    Returns:
        HttpResponse: Rendered journalist list page.
    """
    journalists = User.objects.filter(role=User.Role.JOURNALIST).order_by("username")
    followed_ids = set(request.user.subscribed_journalists.values_list("id", flat=True))
    context = {"journalists": journalists, "followed_ids": followed_ids}
    return render(request, "core/journalist_list.html", context)


@login_required
def my_subscriptions(request):
    """
    Display a summary of the current user's publisher subscriptions and journalist follows.

    Args:
        request: Django HttpRequest.

    Returns:
        HttpResponse: Rendered subscriptions page.
    """
    publishers = request.user.subscribed_publishers.order_by("name")
    journalists = request.user.subscribed_journalists.order_by("username")

    context = {
        "publishers": publishers,
        "journalists": journalists,
    }
    return render(request, "core/my_subscriptions.html", context)


@login_required
def toggle_journalist_follow(request, pk: int):
    """
    Follow/unfollow a journalist user.

    Expects POST. Non-POST requests are redirected back to journalist list.

    Args:
        request: Django HttpRequest.
        pk (int): Journalist user primary key.

    Returns:
        HttpResponseRedirect: Redirect back to journalist list.
    """
    if request.method != "POST":
        return redirect("core:journalist_list")

    journalist = get_object_or_404(User, pk=pk, role=User.Role.JOURNALIST)

    if request.user.pk == journalist.pk:
        return redirect("core:journalist_list")

    if request.user.subscribed_journalists.filter(pk=journalist.pk).exists():
        request.user.subscribed_journalists.remove(journalist)
    else:
        request.user.subscribed_journalists.add(journalist)

    return redirect("core:journalist_list")


@login_required
def journalist_dashboard(request):
    """
    Journalist-only dashboard showing their submitted articles.

    Args:
        request: Django HttpRequest.

    Returns:
        HttpResponse: Rendered journalist dashboard.

    Raises:
        HttpResponseForbidden: If user is not a journalist.
    """
    if request.user.role != User.Role.JOURNALIST:
        return HttpResponseForbidden("Only journalists can view this page.")

    articles = Article.objects.filter(author=request.user).order_by("-created_at")
    return render(request, "core/journalist_dashboard.html", {"articles": articles})


@login_required
def create_article(request):
    """
    Journalist-only view to submit a new article (created as PENDING).

    Args:
        request: Django HttpRequest.

    Returns:
        HttpResponse: Rendered create form on GET; redirect on success.

    Raises:
        HttpResponseForbidden: If user is not a journalist.
    """
    if request.user.role != User.Role.JOURNALIST:
        return HttpResponseForbidden("Only journalists can create articles.")
    
    Publisher.objects.get_or_create(
    name="Independent",
    defaults={"description": "Independent publisher"},
)

    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = Article.Status.PENDING
            article.save()
            return redirect("core:journalist_dashboard")
    else:
        form = ArticleForm()

    return render(request, "core/create_article.html", {"form": form})


@login_required
def editor_queue(request):
    """
    Editor-only review queue showing all pending articles.

    Args:
        request: Django HttpRequest.

    Returns:
        HttpResponse: Rendered editor queue page.

    Raises:
        HttpResponseForbidden: If user is not an editor.
    """
    if request.user.role != User.Role.EDITOR:
        return HttpResponseForbidden("Only editors can view this page.")

    pending_articles = Article.objects.filter(status=Article.Status.PENDING).order_by(
        "-created_at"
    )
    return render(request, "core/editor_queue.html", {"articles": pending_articles})


@login_required
def decide_article(request, pk: int):
    """
    Editor-only action endpoint to approve or reject an article.

    - Approve: sets APPROVED, emails author, emails publisher subscribers, attempts X post
    - Reject: sets REJECTED, saves reason, emails author

    Args:
        request: Django HttpRequest.
        pk (int): Article primary key.

    Returns:
        HttpResponseRedirect: Redirect back to editor queue.

    Raises:
        HttpResponseForbidden: If user is not an editor.
    """
    if request.user.role != User.Role.EDITOR:
        return HttpResponseForbidden("Only editors can review articles.")

    article = get_object_or_404(Article, pk=pk)

    if request.method != "POST":
        return redirect("core:editor_queue")

    action = request.POST.get("action")
    reason = request.POST.get("reason", "").strip()

    if action == "approve":
        article.status = Article.Status.APPROVED
        article.decision_reason = ""
        article.decided_at = timezone.now()
        article.save()

        subject = f"Article approved: {article.title}"
        body = (
            f"Hi {article.author.username},\n\n"
            f"Good news — your article '{article.title}' has been approved.\n\n"
            f"Publisher: {article.publisher.name}\n\n"
            "Regards,\nNews App Editor"
        )
        if article.author.email:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [article.author.email])

        subscriber_emails = (
            User.objects.filter(subscribed_publishers=article.publisher)
            .exclude(pk=article.author.pk)
            .exclude(email__isnull=True)
            .exclude(email__exact="")
            .values_list("email", flat=True)
            .distinct()
        )
        subscriber_emails = list(subscriber_emails)

        if subscriber_emails:
            subject = f"New article from {article.publisher.name}: {article.title}"
            body = (
                "Hi,\n\n"
                f"A new article has been published by {article.publisher.name}:\n\n"
                f"Title: {article.title}\n"
                f"Author: {article.author.username}\n\n"
                f"Read it here: http://127.0.0.1:8000/articles/{article.pk}/\n\n"
                "Regards,\nNews App"
            )
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, subscriber_emails)
            messages.info(
                request,
                f"Subscribers notified ({len(subscriber_emails)} email(s)).",
            )

        posted = post_article_to_x(article, request)
        if posted:
            messages.info(request, "Posted to X.")
        else:
            messages.info(request, "X post skipped or failed.")

        messages.success(request, "Article approved and notifications sent.")

    elif action == "reject":
        article.status = Article.Status.REJECTED
        article.decision_reason = reason
        article.decided_at = timezone.now()
        article.save()

        subject = f"Article rejected: {article.title}"
        body = (
            f"Hi {article.author.username},\n\n"
            f"Your article '{article.title}' was not approved.\n\n"
            f"Reason:\n{reason if reason else 'No reason provided.'}\n\n"
            "Regards,\nNews App Editor"
        )
        if article.author.email:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [article.author.email])

        messages.error(request, "Article rejected and author notified.")

    else:
        messages.warning(request, "Invalid action.")

    return redirect("core:editor_queue")