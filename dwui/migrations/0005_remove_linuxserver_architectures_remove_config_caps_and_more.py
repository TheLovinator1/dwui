# Generated by Django 5.1.7 on 2025-03-30 00:07
from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import migrations

if TYPE_CHECKING:
    from django.db.migrations.operations.base import Operation


class Migration(migrations.Migration):
    """Migration to remove Linuxserver and Config models and their related fields.

    This migration also removes several related models such as Architecture, Cap, Changelog, etc.
    """

    dependencies: list[tuple[str, str]] = [
        ("dwui", "0004_adminsettings_default_config_path_and_more"),
    ]

    operations: list[Operation] = [
        migrations.RemoveField(
            model_name="linuxserver",
            name="architectures",
        ),
        migrations.RemoveField(
            model_name="config",
            name="caps",
        ),
        migrations.RemoveField(
            model_name="linuxserver",
            name="changelog",
        ),
        migrations.RemoveField(
            model_name="config",
            name="custom",
        ),
        migrations.RemoveField(
            model_name="config",
            name="devices",
        ),
        migrations.RemoveField(
            model_name="config",
            name="env_vars",
        ),
        migrations.RemoveField(
            model_name="config",
            name="hostname",
        ),
        migrations.RemoveField(
            model_name="config",
            name="mac_address",
        ),
        migrations.RemoveField(
            model_name="config",
            name="ports",
        ),
        migrations.RemoveField(
            model_name="config",
            name="security_opt",
        ),
        migrations.RemoveField(
            model_name="config",
            name="volumes",
        ),
        migrations.RemoveField(
            model_name="linuxserver",
            name="config",
        ),
        migrations.DeleteModel(
            name="ImagesResponse",
        ),
        migrations.RemoveField(
            model_name="linuxserver",
            name="tags",
        ),
        migrations.DeleteModel(
            name="Architecture",
        ),
        migrations.DeleteModel(
            name="Cap",
        ),
        migrations.DeleteModel(
            name="Changelog",
        ),
        migrations.DeleteModel(
            name="Custom",
        ),
        migrations.DeleteModel(
            name="EnvVar",
        ),
        migrations.DeleteModel(
            name="Hostname",
        ),
        migrations.DeleteModel(
            name="MACAddress",
        ),
        migrations.DeleteModel(
            name="Port",
        ),
        migrations.DeleteModel(
            name="SecurityOpt",
        ),
        migrations.DeleteModel(
            name="Device",
        ),
        migrations.DeleteModel(
            name="Config",
        ),
        migrations.DeleteModel(
            name="Linuxserver",
        ),
        migrations.DeleteModel(
            name="Tag",
        ),
    ]
