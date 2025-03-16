from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler
from django.core.management import execute_from_command_line
from django.http import HttpRequest, HttpResponse
from django.urls import path
from dotenv import load_dotenv

if TYPE_CHECKING:
    from django.urls.resolvers import URLPattern

load_dotenv()

LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

settings.configure(
    ROOT_URLCONF=__name__,
    DEBUG=os.getenv(key="DJANGO_DEBUG", default="False").lower() == "true",
    SECRET_KEY=os.getenv(key="DJANGO_SECRET_KEY"),
    ALLOWED_HOSTS=["*"],
    LOGGING=LOGGING,
)


def index(request: HttpRequest) -> HttpResponse:
    """Index view for the agent.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    return HttpResponse("Agent is running!")


urlpatterns: list[URLPattern] = [path("", index)]
application = WSGIHandler()

if __name__ == "__main__":
    execute_from_command_line()
