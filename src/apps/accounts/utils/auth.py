from typing import Dict, Optional

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def generate_tokens_for_user(user: User) -> Dict[str, str]:
    """
    Generate JWT access and refresh tokens for a user.

    Args:
        user: User instance

    Returns:
        Dictionary containing access and refresh tokens
    """
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def get_user_from_token(token_string: str) -> Optional[User]:
    """
    Get user from a refresh token.

    Args:
        token_string: The refresh token string

    Returns:
        User instance if valid, None otherwise
    """
    try:
        token = RefreshToken(token_string)
        user_id = token.payload.get("user_id")
        return User.objects.get(id=user_id)
    except Exception:
        return None
