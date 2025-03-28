from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import requests
from django.db import transaction

from dwui.models import Linuxserver

logger: logging.Logger = logging.getLogger("dwui")


def download_json() -> dict[str, str] | None:
    """Download JSON data from the LinuxServer.io API.

    Returns:
        dict[str, str] | None: Dictionary containing the JSON data.
    """
    url = "https://api.linuxserver.io/api/v1/images?include_config=true&include_deprecated=true"

    try:
        response: requests.Response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.HTTPError:
        logger.exception("HTTP error occurred")
        return None
    except requests.RequestException:
        logger.exception("Request failed")
        return None
    return dict(response.json())


def add_data_to_model(data: dict[str, Any]) -> None:
    """Add data to the model.

      Example data:
      ```json
          {
            "data": {
                "repositories": {
                    "linuxserver": []
                }
            }
        }
    ```

    Args:
          data (dict[bytes, bytes]): Dictionary containing the JSON data.
    """
    data = data.get("data", {})
    if not data:
        logger.warning("No data found in the response")
        return

    repos = data.get("repositories", {})
    if not repos:
        logger.warning("No repositories found in the data")
        return

    linux_servers = repos.get("linuxserver", {})
    if not linux_servers:
        logger.warning("No LinuxServer repositories found in the data")
        return

    for container in linux_servers:
        try:
            with transaction.atomic():
                # Extract version_timestamp or set default value before creating the instance
                version_timestamp = None
                version_timestamp_str = container.get("version_timestamp")
                if version_timestamp_str and isinstance(version_timestamp_str, str):
                    try:
                        version_timestamp = datetime.fromisoformat(version_timestamp_str)
                    except ValueError:
                        logger.warning("Invalid version_timestamp format: %s, using current time", version_timestamp_str)
                        version_timestamp = datetime.now(tz=UTC)
                else:
                    version_timestamp = datetime.now(tz=UTC)

                # Use get_or_create with default values for non-nullable fields
                linuxserver, _created = Linuxserver.objects.get_or_create(
                    name=container["name"],
                    defaults={
                        "version_timestamp": version_timestamp,
                        "description": container.get("description", ""),
                        "version": container.get("version", ""),
                        "category": container.get("category", ""),
                        "stars": container.get("stars", 0),
                    },
                )

                # If instance is newly created, version_timestamp is already set
                # Otherwise, update via from_dict
                linuxserver.from_dict(container)

                logger.info("Successfully imported data for %s", linuxserver.name)
        except Exception:
            logger.exception("Error while processing container %s", container.get("name", "unknown"))
