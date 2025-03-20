from __future__ import annotations

import logging
import os
import sys
from typing import TYPE_CHECKING

import django
from django.core.handlers.wsgi import WSGIHandler
from django.http import HttpRequest, HttpResponse
from django.urls import path

if TYPE_CHECKING:
    from django.urls.resolvers import URLPattern

logger: logging.Logger = logging.getLogger("dwui.agent")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()


def index(request: HttpRequest) -> HttpResponse:
    """Index view for the agent.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    return HttpResponse("Agent is running!")


urlpatterns: list[URLPattern] = [path("", index, name="index")]
application: WSGIHandler = WSGIHandler()

if __name__ == "__main__":
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        msg = (
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
        raise ImportError(msg) from exc
    execute_from_command_line(sys.argv)
