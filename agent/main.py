from __future__ import annotations

import os
from typing import TYPE_CHECKING

import django
from django.core.handlers.wsgi import WSGIHandler
from django.core.management import execute_from_command_line
from django.http import HttpRequest, HttpResponse
from django.urls import path

if TYPE_CHECKING:
    from django.urls.resolvers import URLPattern

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
    execute_from_command_line()
