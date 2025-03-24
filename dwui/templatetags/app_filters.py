"""Custom template filters for the Docker Web UI application."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from docker.models.containers import Container

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


@register.filter
def groupby(value: list[Container]) -> list[tuple[str, list[Container]]]:
    """Group containers by their labels.

    Args:
        value: A list of Docker containers

    Returns:
        A list of tuples, where each tuple contains a label and a list of containers
    """
    grouped = defaultdict(list)
    for item in value:
        labels: dict[str, str] = item.attrs.get("Config", {}).get("Labels", {})
        key: str = labels.get("com.docker.compose.project", "default")
        grouped[key].append(item)
    return list(grouped.items())
