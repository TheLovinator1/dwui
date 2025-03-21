from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

ROOT_URLCONF = "main"
DEBUG: bool = os.getenv("DJANGO_DEBUG", "").lower() == "true"
ALLOWED_HOSTS: list[str] = ["*"]
SECRET_KEY: str | None = os.getenv(key="DJANGO_SECRET_KEY")
DWUI_AGENT_API_URL: str = os.getenv(key="DWUI_AGENT_API_URL", default="http://agent:8000")

if not SECRET_KEY:
    msg = "The DJANGO_SECRET_KEY environment variable must be set."
    raise ValueError(msg)

if not DWUI_AGENT_API_URL:
    msg = "The DWUI_AGENT_API_URL environment variable must be set."
    raise ValueError(msg)

LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
