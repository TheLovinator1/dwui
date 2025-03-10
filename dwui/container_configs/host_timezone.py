from __future__ import annotations

import os
from pathlib import Path


def get_host_timezone() -> str:
    """Detect the host system's timezone.

    Returns:
        str: The detected timezone or "Etc/UTC" as fallback.
    """
    if tz := os.environ.get("TZ"):
        return tz

    try:
        if Path("/etc/timezone").is_file():
            timezone: str = Path("/etc/timezone").read_text(encoding="utf-8").strip()
            if timezone:
                return timezone
    except OSError:
        pass

    return "Etc/UTC"
