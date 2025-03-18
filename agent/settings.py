from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

ROOT_URLCONF = "main"
DEBUG: bool = os.getenv("DJANGO_DEBUG", "").lower() == "true"
ALLOWED_HOSTS: list[str] = ["*"]
SECRET_KEY: str | None = os.getenv(key="DJANGO_SECRET_KEY")


if SECRET_KEY is None:
    msg = "The DJANGO_SECRET_KEY environment variable must be set."
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
