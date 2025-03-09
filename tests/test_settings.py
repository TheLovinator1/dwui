from __future__ import annotations

from dwui.settings import MIDDLEWARE  # noqa: TID251


def test_middleware_order() -> None:
    """Test that LoginRequiredMiddleware is placed after AuthenticationMiddleware."""
    # Check that both middlewares are included in settings
    auth_middleware = "django.contrib.auth.middleware.AuthenticationMiddleware"
    login_required_middleware = "django.contrib.auth.middleware.LoginRequiredMiddleware"

    assert auth_middleware in MIDDLEWARE, "AuthenticationMiddleware is missing from MIDDLEWARE"
    assert login_required_middleware in MIDDLEWARE, "LoginRequiredMiddleware is missing from MIDDLEWARE"

    # Get the indices of both middlewares
    auth_index: int = MIDDLEWARE.index(auth_middleware)
    login_required_index: int = MIDDLEWARE.index(login_required_middleware)

    # Check that LoginRequiredMiddleware comes after AuthenticationMiddleware
    assert auth_index < login_required_index, (
        f"LoginRequiredMiddleware (at position {login_required_index}) must be placed "
        f"after AuthenticationMiddleware (at position {auth_index})"
    )
