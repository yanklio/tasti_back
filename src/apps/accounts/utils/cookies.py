from django.conf import settings
from django.http import HttpResponse


def set_refresh_token_cookie(response: HttpResponse, refresh_token: str) -> None:
    """
    Set refresh token in httpOnly cookie with consistent settings.

    Args:
        response: Django HttpResponse object
        refresh_token: JWT refresh token string
    """
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=getattr(settings, "REFRESH_TOKEN_MAX_AGE", 86400),  # 1 day default
        httponly=True,
        secure=getattr(settings, "COOKIE_SECURE", not settings.DEBUG),
        samesite=getattr(
            settings, "COOKIE_SAMESITE", "Lax" if settings.DEBUG else "None"
        ),
        path="/",
    )


def delete_refresh_token_cookie(response: HttpResponse) -> None:
    """
    Delete refresh token cookie.

    Args:
        response: Django HttpResponse object
    """
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite=getattr(
            settings, "COOKIE_SAMESITE", "Lax" if settings.DEBUG else "None"
        ),
    )


def get_refresh_token_from_request(request) -> str | None:
    """
    Extract refresh token from request cookies.

    Args:
        request: Django request object

    Returns:
        Refresh token string if found, None otherwise
    """
    return request.COOKIES.get("refresh_token")
