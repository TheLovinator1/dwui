from __future__ import annotations

from django.apps import AppConfig


class DWUIAppConfig(AppConfig):
    """Configuration for dwui application.

    Attributes:
        default_auto_field (str): Specifies the type of auto-incrementing primary key field to use for models in this app.
        name (str): The name of the application.
    """

    default_auto_field: str = "django.db.models.BigAutoField"
    name = "dwui"
