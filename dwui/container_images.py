"""Container images configuration module for Docker Web UI."""

from __future__ import annotations

from typing import Literal, TypedDict


class VolumeConfig(TypedDict):
    """Type definition for volume configuration."""

    source: str  # Source path on host
    target: str  # Target path in container
    description: str  # User-friendly description of what this volume stores
    required: bool  # Whether this volume is required for the container to function properly


class PortConfig(TypedDict):
    """Type definition for port configuration."""

    host: str  # Host port
    container: str  # Container port
    protocol: Literal["tcp", "udp"]  # Protocol
    description: str  # User-friendly description of what this port is for


class EnvVarConfig(TypedDict):
    """Type definition for environment variable configuration."""

    name: str  # Environment variable name
    default: str | None  # Default value (None if required without default)
    description: str  # User-friendly description of what this variable does
    required: bool  # Whether this variable is required
    options: list[str] | None  # Possible options for the variable (e.g., for dropdowns)


class ContainerImageConfig(TypedDict):
    """Type definition for container image configuration."""

    name: str  # Display name
    image: str  # Docker image name
    description: str  # Description of the container
    volumes: list[VolumeConfig]  # Volume configurations
    ports: list[PortConfig]  # Port configurations
    env_vars: list[EnvVarConfig]  # Environment variable configurations
    category: str  # Category of the container (e.g., "Media Server", "Storage")


# Container images configuration
CONTAINER_IMAGES: list[ContainerImageConfig] = [
    {
        "name": "LinuxServer Plex",
        "image": "linuxserver/plex",
        "description": "Plex Media Server",
        "category": "Media Server",
        "volumes": [
            {"source": "/path/to/config", "target": "/config", "description": "Configuration files", "required": True},
            {"source": "/path/to/media", "target": "/media", "description": "Media files", "required": True},
        ],
        "ports": [{"host": "32400", "container": "32400", "protocol": "tcp", "description": "Web UI access"}],
        "env_vars": [
            {"name": "PUID", "default": "1000", "description": "User ID", "required": True, "options": None},
            {"name": "PGID", "default": "1000", "description": "Group ID", "required": True, "options": None},
            {
                "name": "VERSION",
                "default": "latest",
                "description": "Plex version",
                "required": False,
                "options": ["latest", "public", "beta"],
            },
        ],
    },
    {
        "name": "LinuxServer Nextcloud",
        "image": "linuxserver/nextcloud",
        "description": "Personal cloud storage",
        "category": "Storage",
        "volumes": [
            {"source": "/path/to/config", "target": "/config", "description": "Configuration files", "required": True},
            {"source": "/path/to/data", "target": "/data", "description": "User data", "required": True},
        ],
        "ports": [
            {"host": "443", "container": "443", "protocol": "tcp", "description": "HTTPS web access"},
            {"host": "80", "container": "80", "protocol": "tcp", "description": "HTTP web access"},
        ],
        "env_vars": [
            {"name": "PUID", "default": "1000", "description": "User ID", "required": True, "options": None},
            {"name": "PGID", "default": "1000", "description": "Group ID", "required": True, "options": None},
        ],
    },
    {
        "name": "LinuxServer Jellyfin",
        "image": "linuxserver/jellyfin",
        "description": "Media server",
        "category": "Media Server",
        "volumes": [
            {"source": "/path/to/config", "target": "/config", "description": "Configuration files", "required": True},
            {"source": "/path/to/media", "target": "/media", "description": "Media files", "required": True},
        ],
        "ports": [{"host": "8096", "container": "8096", "protocol": "tcp", "description": "Web UI access"}],
        "env_vars": [
            {"name": "PUID", "default": "1000", "description": "User ID", "required": True, "options": None},
            {"name": "PGID", "default": "1000", "description": "Group ID", "required": True, "options": None},
        ],
    },
    {
        "name": "LinuxServer Heimdall",
        "image": "linuxserver/heimdall",
        "description": "Application dashboard",
        "category": "Dashboard",
        "volumes": [{"source": "/path/to/config", "target": "/config", "description": "Configuration files", "required": True}],
        "ports": [
            {"host": "80", "container": "80", "protocol": "tcp", "description": "HTTP web access"},
            {"host": "443", "container": "443", "protocol": "tcp", "description": "HTTPS web access"},
        ],
        "env_vars": [
            {"name": "PUID", "default": "1000", "description": "User ID", "required": True, "options": None},
            {"name": "PGID", "default": "1000", "description": "Group ID", "required": True, "options": None},
        ],
    },
    {
        "name": "LinuxServer Calibre-web",
        "image": "linuxserver/calibre-web",
        "description": "E-book manager",
        "category": "Media Manager",
        "volumes": [
            {"source": "/path/to/config", "target": "/config", "description": "Configuration files", "required": True},
            {"source": "/path/to/books", "target": "/books", "description": "Books directory", "required": True},
        ],
        "ports": [{"host": "8083", "container": "8083", "protocol": "tcp", "description": "Web UI access"}],
        "env_vars": [
            {"name": "PUID", "default": "1000", "description": "User ID", "required": True, "options": None},
            {"name": "PGID", "default": "1000", "description": "Group ID", "required": True, "options": None},
            {
                "name": "DOCKER_MODS",
                "default": "linuxserver/calibre-web:calibre",
                "description": "Optional Calibre integration",
                "required": False,
                "options": None,
            },
        ],
    },
]


def get_container_images() -> list[ContainerImageConfig]:
    """Return the list of container images.

    Returns:
        List[ContainerImageConfig]: List of container images with their configuration.
    """
    return CONTAINER_IMAGES


def get_container_image_by_name(image_name: str) -> ContainerImageConfig | None:
    """Get container image configuration by image name.

    Args:
        image_name (str): The name of the image to look up.

    Returns:
        Optional[ContainerImageConfig]: The container image configuration if found, None otherwise.
    """
    for image in CONTAINER_IMAGES:
        if image["image"] == image_name:
            return image
    return None


def get_categories() -> list[str]:
    """Get a list of unique container categories.

    Returns:
        List[str]: List of unique container categories.
    """
    categories = set()
    categories.update(image["category"] for image in CONTAINER_IMAGES)
    return sorted(categories)
