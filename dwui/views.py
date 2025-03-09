from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_not_required  # pyright: ignore[reportAttributeAccessIssue]
from django.shortcuts import render

from dwui.docker_helper import DockerClient

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


@login_not_required
def index(request: HttpRequest) -> HttpResponse:
    """Render the home page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    with DockerClient() as client:
        version: dict = client.version()
        containers = client.containers.list(all=True)

    context = {
        "version": version,
        "containers": containers,
    }

    return render(request, "index.html", context)
