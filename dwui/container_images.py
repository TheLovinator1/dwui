"""Container images configuration module for Docker Web UI."""

from __future__ import annotations

from dwui.container_config import ContainerImageConfig, EnvVarConfig, PortConfig, VolumeConfig
from dwui.container_configs.loader import get_all_container_configs

# Container images configuration
CONTAINER_IMAGES: list[ContainerImageConfig] = [
    ContainerImageConfig.with_common_env_vars(
        name="LinuxServer Plex",
        image="linuxserver/plex",
        description="Plex Media Server",
        category="Media Server",
        volumes=[
            VolumeConfig(source="/path/to/config", target="/config", description="Configuration files"),
            VolumeConfig(source="/path/to/media", target="/media", description="Media files"),
        ],
        ports=[PortConfig(host="32400", container="32400", protocol="tcp", description="Web UI access")],
        env_vars=[
            EnvVarConfig(
                name="VERSION",
                default="latest",
                description="Plex version",
                required=False,
                options=["latest", "public", "beta"],
            ),
        ],
    ),
    ContainerImageConfig.with_common_env_vars(
        name="LinuxServer Nextcloud",
        image="linuxserver/nextcloud",
        description="Personal cloud storage",
        category="Storage",
        volumes=[
            VolumeConfig(source="/path/to/config", target="/config", description="Configuration files"),
            VolumeConfig(source="/path/to/data", target="/data", description="User data"),
        ],
        ports=[
            PortConfig(host="443", container="443", protocol="tcp", description="HTTPS web access"),
            PortConfig(host="80", container="80", protocol="tcp", description="HTTP web access"),
        ],
    ),
    ContainerImageConfig.with_common_env_vars(
        name="LinuxServer Jellyfin",
        image="linuxserver/jellyfin",
        description="Media server",
        category="Media Server",
        volumes=[
            VolumeConfig(source="/path/to/config", target="/config", description="Configuration files"),
            VolumeConfig(source="/path/to/media", target="/media", description="Media files"),
        ],
        ports=[PortConfig(host="8096", container="8096", protocol="tcp", description="Web UI access")],
    ),
    ContainerImageConfig.with_common_env_vars(
        name="LinuxServer Heimdall",
        image="linuxserver/heimdall",
        description="Application dashboard",
        category="Dashboard",
        volumes=[VolumeConfig(source="/path/to/config", target="/config", description="Configuration files")],
        ports=[
            PortConfig(host="80", container="80", protocol="tcp", description="HTTP web access"),
            PortConfig(host="443", container="443", protocol="tcp", description="HTTPS web access"),
        ],
    ),
    ContainerImageConfig.with_common_env_vars(
        name="LinuxServer Calibre-web",
        image="linuxserver/calibre-web",
        description="E-book manager",
        category="Media Manager",
        volumes=[
            VolumeConfig(source="/path/to/config", target="/config", description="Configuration files"),
            VolumeConfig(source="/path/to/books", target="/books", description="Books directory"),
        ],
        ports=[PortConfig(host="8083", container="8083", protocol="tcp", description="Web UI access")],
        env_vars=[
            EnvVarConfig(
                name="DOCKER_MODS",
                default="linuxserver/calibre-web:calibre",
                description="Optional Calibre integration",
                required=False,
            ),
        ],
    ),
]

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
