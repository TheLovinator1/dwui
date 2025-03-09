from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from platformdirs import user_data_dir

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = Path(user_data_dir(appname="dwui", appauthor="TheLovinator", roaming=True, ensure_exists=True))

SECRET_KEY: str | None = os.getenv(key="DJANGO_SECRET_KEY")
if SECRET_KEY is None:
    msg = "DJANGO_SECRET_KEY environment variable is not set. You can generate one using `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`"  # noqa: E501
    raise OSError(msg)

DEBUG: bool = os.getenv(key="DJANGO_DEBUG", default="False").lower() == "true"
ALLOWED_HOSTS: list[str] = os.getenv(key="DJANGO_ALLOWED_HOSTS", default="127.0.0.1").split(",")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DECIMAL_SEPARATOR = ","
THOUSAND_SEPARATOR = " "
INTERNAL_IPS: list[str] = ["127.0.0.1", "::1"]
SITE_ID = 1
WSGI_APPLICATION = "dwui.wsgi.application"
ROOT_URLCONF = "dwui.urls"

INSTALLED_APPS: list[str] = [
    "dwui.apps.DWUIAppConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES: dict[str, dict[str, str | Path | dict[str, str]]] = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "dwui-db.sqlite3",
        "OPTIONS": {
            "init_command": "PRAGMA journal_mode=wal; PRAGMA synchronous=1; PRAGMA mmap_size=134217728; PRAGMA journal_size_limit=67108864; PRAGMA cache_size=2000;",  # noqa: E501
        },
    },
}

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

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
        "asyncio": {  # Hide "Using selector: SelectSelector" spam
            "level": "WARNING",
        },
    },
}

ENABLE_DEBUG_TOOLBAR: bool = DEBUG and "test" not in sys.argv
if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    DEBUG_TOOLBAR_CONFIG: dict[str, Any] = {
        "ROOT_TAG_EXTRA_ATTRS": "hx-preserve",
        "SQL_WARNING_THRESHOLD": 100,
        "UPDATE_ON_FETCH": True,
    }
