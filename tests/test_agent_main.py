from __future__ import annotations

import importlib
import os
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from django.test import RequestFactory, override_settings
from django.urls import resolve

from agent.main import application, index, urlpatterns

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponse


@pytest.fixture
def request_factory() -> RequestFactory:
    """Create a request factory for testing views.

    Returns:
        RequestFactory: A Django RequestFactory instance.
    """
    return RequestFactory()


def test_agent_index_view(request_factory: RequestFactory) -> None:
    """Test the agent's index view."""
    request: WSGIRequest = request_factory.get("/")
    response: HttpResponse = index(request)

    assert response.status_code == 200
    assert "Agent is running!" in response.content.decode()


@override_settings(ROOT_URLCONF="agent.main")
def test_urlpatterns() -> None:
    """Test that the URL patterns are correctly defined."""
    assert len(urlpatterns) >= 1
    assert resolve("/").func.__name__ == index.__name__


def test_wsgi_application() -> None:
    """Test that the WSGI application is correctly defined."""
    assert application is not None
    assert callable(application)


def test_django_settings_module_env_var() -> None:
    """Test the DJANGO_SETTINGS_MODULE env var is correctly set in the module."""
    original_value: str | None = os.environ.get("DJANGO_SETTINGS_MODULE")

    try:
        with patch.dict(os.environ, clear=True):
            import agent.main  # noqa: PLC0415

            importlib.reload(agent.main)
            assert os.environ.get("DJANGO_SETTINGS_MODULE") == "settings"
    finally:
        if original_value:
            os.environ["DJANGO_SETTINGS_MODULE"] = original_value
        elif "DJANGO_SETTINGS_MODULE" in os.environ:
            del os.environ["DJANGO_SETTINGS_MODULE"]
