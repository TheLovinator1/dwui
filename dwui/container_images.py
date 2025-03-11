"""Container images configuration module for Docker Web UI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dwui.container_configs.loader import get_all_container_configs

if TYPE_CHECKING:
    from dwui.container_config import ContainerImageConfig

# Container images configuration
CONTAINER_IMAGES: list[ContainerImageConfig] = []

# Add all imported container configurations
CONTAINER_IMAGES.extend(get_all_container_configs())


def get_container_images() -> list[dict]:
    """Return the list of container images.

    Returns:
        List[dict]: List of container images with their configuration as dictionaries.
    """
    return [image.to_dict() for image in CONTAINER_IMAGES]


def get_container_image_by_name(image_name: str) -> dict | None:
    """Get container image configuration by image name.

    Args:
        image_name (str): The name of the image to look up.

    Returns:
        Optional[dict]: The container image configuration if found, None otherwise.
    """
    for image in CONTAINER_IMAGES:
        if image.image == image_name:
            return image.to_dict()
    return None


def get_categories() -> list[str]:
    """Get a list of unique container categories.

    Returns:
        List[str]: List of unique container categories.
    """
    categories = set()
    for image in CONTAINER_IMAGES:
        if "," in image.category:
            # Split multi-categories and add each one
            categories.update(category.strip() for category in image.category.split(","))
        else:
            categories.add(image.category)
    return sorted(categories)
