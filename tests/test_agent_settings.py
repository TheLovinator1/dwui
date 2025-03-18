from __future__ import annotations

import importlib
import importlib.util
import os
from unittest.mock import patch

from agent import settings


def test_debug_setting_true_when_env_var_is_true() -> None:
    """Test that DEBUG is True when DJANGO_DEBUG env var is 'true'."""
    with patch.dict(os.environ, {"DJANGO_DEBUG": "true"}, clear=True):
        importlib.reload(settings)
        assert settings.DEBUG is True


def test_debug_setting_false_when_env_var_is_false() -> None:
    """Test that DEBUG is False when DJANGO_DEBUG env var is 'false'."""
    with patch.dict(os.environ, {"DJANGO_DEBUG": "false"}, clear=True):
        importlib.reload(settings)
        assert settings.DEBUG is False


def test_allowed_hosts() -> None:
    """Test that ALLOWED_HOSTS contains '*'."""
    assert "*" in settings.ALLOWED_HOSTS
    assert isinstance(settings.ALLOWED_HOSTS, list)


def test_root_urlconf() -> None:
    """Test that ROOT_URLCONF is properly set."""
    assert settings.ROOT_URLCONF == "main"
    assert importlib.util.find_spec(settings.ROOT_URLCONF) is not None


def test_logging_config() -> None:
    """Test that LOGGING is properly configured."""
    assert "version" in settings.LOGGING
    assert settings.LOGGING["version"] == 1

    assert "handlers" in settings.LOGGING
    assert "console" in settings.LOGGING["handlers"]

    assert "loggers" in settings.LOGGING
    assert "" in settings.LOGGING["loggers"]

    root_logger = settings.LOGGING["loggers"][""]
    assert "handlers" in root_logger
    assert "console" in root_logger["handlers"]
    assert root_logger["level"] == "DEBUG"
