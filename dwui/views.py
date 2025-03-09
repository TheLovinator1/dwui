from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_not_required  # pyright: ignore[reportAttributeAccessIssue]
from django.shortcuts import render

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
    return render(request, "index.html")
