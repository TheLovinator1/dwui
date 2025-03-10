from __future__ import annotations

import pytest
from django.urls import resolve, reverse


@pytest.mark.parametrize(
    ("url_name", "kwargs"),
    [
        ("index", {}),
        ("new_container", {}),
        ("container_details", {"container_id": "test"}),
        ("start_container", {"container_id": "test"}),
        ("stop_container", {"container_id": "test"}),
        ("restart_container", {"container_id": "test"}),
        ("remove_container", {"container_id": "test"}),
        ("update_container", {"container_id": "test"}),
        ("image_config", {}),
        ("account_login", {}),
        ("account_logout", {}),
    ],
)
def test_url_resolves(url_name: str, kwargs: dict[str, str]) -> None:
    """Test that the URL resolves to the correct view name.

    Args:
        url_name (str): The name of the URL pattern.
        kwargs (dict[str, str]): The keyword arguments for the URL pattern.
    """
    url: str = reverse(url_name, kwargs=kwargs)
    assert resolve(url).view_name == url_name
