from __future__ import annotations

import logging

from django.contrib.auth.models import AbstractUser
from django.db import models

logger: logging.Logger = logging.getLogger("dwui")


class CustomUser(AbstractUser):
    """CustomUser model that extends the default Django AbstractUser.

    This model can be used to add additional fields or methods to the default user model provided by Django.

    Attributes:
        Inherits all attributes from AbstractUser.
    """


class AdminSettings(models.Model):
    """A Django model representing the administrative settings for a web application.

    Attributes:
        site_name (str): The name of the site.
        enable_notifications (bool): Flag to enable or disable notifications.
        apprise_urls (str): A newline-separated list of URLs for notifications.
        default_data_path (str): Default path for container data storage (e.g., HDD).
        default_config_path (str): Default path for container configuration storage (e.g., NVMe).

    Methods:
        __str__(): Returns the site name as the string representation of the model.
    """

    site_id = models.AutoField(primary_key=True, help_text="Site ID")
    site_name = models.TextField(blank=True, max_length=100, default="dwui", help_text="Site Name")
    enable_notifications = models.BooleanField(default=False, help_text="Send notifications to apprise URLs")
    apprise_urls = models.TextField(blank=True, help_text="Newline separated list of apprise URLs")
    default_data_path = models.TextField(blank=True, default="", help_text="Default path for container data storage (e.g., HDD)")
    default_config_path = models.TextField(
        blank=True,
        default="",
        help_text="Default path for container configuration storage (e.g., NVMe)",
    )

    def __str__(self) -> str:
        """Return the site name."""
        return self.site_name
