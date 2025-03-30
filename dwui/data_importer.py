from __future__ import annotations

import json
import logging
from pathlib import Path

import requests

logger: logging.Logger = logging.getLogger("dwui")

CONTAINER_CONFIGS_DIR: Path = Path(__file__).resolve().parent / "container_configs"
CONTAINER_CONFIGS_DIR.mkdir(exist_ok=True)
LINUXSERVER_API_URL: str = "https://api.linuxserver.io/api/v1/images?include_config=true&include_deprecated=true"


def fetch_and_store_container_data() -> None:
    """Fetch container data from the LinuxServer API and store it as JSON files."""
    response: requests.Response = requests.get(LINUXSERVER_API_URL, timeout=10)
    response.raise_for_status()

    data = response.json()
    repositories = data.get("data", {}).get("repositories", {}).get("linuxserver", [])

    if not repositories:
        logger.warning("No repositories found in the response")
        return

    for repo in repositories:
        name = repo.get("name")
        if not name:
            logger.warning("No name found for repository, skipping")
            continue

        # Save each repository's data into a separate JSON file
        file_path: Path = CONTAINER_CONFIGS_DIR / "lsio" / f"{name}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        with file_path.open("w", encoding="utf-8") as json_file:
            json.dump(repo, json_file, indent=4)

        logger.info("Saved repository data for %s to %s", name, file_path)
