# Generated by Django 5.1.7 on 2025-03-26 04:35
from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import migrations, models

if TYPE_CHECKING:
    from django.db.migrations.operations.base import Operation


class Migration(migrations.Migration):
    """Migration to remove the admin_email field from AdminSettings and add apprise_urls."""

    dependencies: list[tuple[str, str]] = [
        ("dwui", "0002_adminsettings"),
    ]

    operations: list[Operation] = [
        migrations.RemoveField(
            model_name="adminsettings",
            name="admin_email",
        ),
        migrations.AddField(
            model_name="adminsettings",
            name="apprise_urls",
            field=models.TextField(blank=True, help_text="Newline separated list of apprise URLs"),
        ),
        migrations.AlterField(
            model_name="adminsettings",
            name="enable_notifications",
            field=models.BooleanField(default=False, help_text="Send notifications to apprise URLs"),
        ),
        migrations.AlterField(
            model_name="adminsettings",
            name="site_name",
            field=models.TextField(blank=True, default="dwui", help_text="Site Name", max_length=100),
        ),
    ]
