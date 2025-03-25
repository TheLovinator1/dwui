from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


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
        admin_email (str): The email address of the site administrator.
        enable_notifications (bool): A flag indicating whether notifications are enabled.

    Methods:
        __str__(): Returns the site name as the string representation of the model.
    """

    site_name = models.CharField(max_length=100)
    admin_email = models.EmailField()
    enable_notifications = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Return the site name."""
        return self.site_name
