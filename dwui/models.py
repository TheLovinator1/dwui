from __future__ import annotations

from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """CustomUser model that extends the default Django AbstractUser.

    This model can be used to add additional fields or methods to the default user model provided by Django.

    Attributes:
        Inherits all attributes from AbstractUser.
    """
