from __future__ import annotations

from typing import TYPE_CHECKING

from dwui.models import AdminSettings

if TYPE_CHECKING:
    from django.http import HttpRequest


def site_name(request: HttpRequest) -> dict[str, str]:
    """Add site_name to the context.

    Args:
        request (HttpRequest): The request object.

    Returns:
        dict[str, str]: A dictionary containing the site_name.
    """
    settings_instance: AdminSettings | None = AdminSettings.objects.first()
    return {"site_name": settings_instance.site_name if settings_instance else "dwui"}
