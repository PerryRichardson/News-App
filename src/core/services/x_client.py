import requests
from django.conf import settings


def post_article_to_x(article, request) -> bool:
    """
    Attempts to post an approved article to X.

    Returns:
        True if we attempted and got a successful response.
        False if disabled or failed for any reason.
    """
    if not getattr(settings, "X_POST_ENABLED", False):
        return False

    bearer_token = getattr(settings, "X_BEARER_TOKEN", "")
    api_url = getattr(settings, "X_API_URL", "")

    if not bearer_token or not api_url:
        return False

    article_url = request.build_absolute_uri(f"/articles/{article.pk}/")
    text = f"{article.title}\n\nRead: {article_url}"

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }
    payload = {"text": text}

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=5,
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False