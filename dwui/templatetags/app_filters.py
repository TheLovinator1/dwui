"""Custom template filters for the Docker Web UI application."""

from __future__ import annotations

from django import template

register = template.Library()


@register.filter
def split(value: str, arg: str) -> list[str]:
    """Split a string by a delimiter.

    Args:
        value: The string to split
        arg: The delimiter to split by

    Returns:
        A list of strings
    """
    return [item.strip() for item in value.split(arg)]
