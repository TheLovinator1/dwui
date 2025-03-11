"""Container configuration classes for Docker Web UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Literal


@dataclass
class VolumeConfig:
    """Class for volume configuration."""

    target: str
    description: str
    required: bool = True
    source: str = ""


@dataclass
class PortConfig:
    """Class for port configuration."""

    internal: str
    desc: str
    optional: bool = False
    external: str = ""
    protocol: Literal["tcp", "udp"] = "tcp"


@dataclass
class EnvVarConfig:
    """Class for environment variable configuration."""

    name: str
    value: str
    description: str
    optional: bool


@dataclass
class DeviceConfig:
    """Class for device configuration."""

    path: str
    host_path: str
    desc: str
    optional: bool = True


@dataclass
class ContainerImageConfig:
    """Class for container image configuration."""

    name: str
    image: str
    description: str
    category: str

    # Additional fields
    application_setup: str = ""
    deprecated: bool = False
    github_url: str = ""
    initial_date: str = ""
    nonroot_supported: bool = False
    project_logo: str = ""
    project_url: str = ""
    readonly_supported: bool = False
    stable: bool = True
    tags: list[dict[str, str]] = field(default_factory=list)
    architectures: list[dict[str, str]] = field(default_factory=list)

    # Container configuration
    volumes: list[VolumeConfig] = field(default_factory=list)
    ports: list[PortConfig] = field(default_factory=list)
    env_vars: list[EnvVarConfig] = field(default_factory=list)
    devices: list[DeviceConfig] = field(default_factory=list)

    COMMON_ENV_VARS: ClassVar[list[EnvVarConfig]] = [
        EnvVarConfig(name="PUID", value="1000", description="User ID", optional=True),
        EnvVarConfig(name="PGID", value="1000", description="Group ID", optional=True),
    ]

    @classmethod
    def create_complete(
        cls,
        name: str,
        image: str,
        description: str,
        category: str,
        initial_date: str = "",
        github_url: str = "",
        project_url: str = "",
        application_setup: str = "",
        project_logo: str = "",
        tags: list[dict[str, str]] | None = None,
        architectures: list[dict[str, str]] | None = None,
        volumes: list[VolumeConfig] | None = None,
        ports: list[PortConfig] | None = None,
        env_vars: list[EnvVarConfig] | None = None,
        devices: list[DeviceConfig] | None = None,
        *,
        nonroot_supported: bool = False,
        readonly_supported: bool = False,
        use_common_env_vars: bool = True,
        stable: bool = True,
        deprecated: bool = False,
    ) -> ContainerImageConfig:
        """Create a complete container image configuration with all available fields.

        Args:
            application_setup (str, optional): The application setup instructions. Defaults to "".
            architectures (list[dict[str, str]], optional): Supported architectures. Defaults to None.
            category (str): The category of the container image.
            deprecated (bool, optional): Whether the image is deprecated. Defaults to False.
            description (str): The description of the container image.
            devices (list[DeviceConfig], optional): Devices for the container. Defaults to None.
            env_vars (list[EnvVarConfig], optional): Environment variables for the container. Defaults to None.
            github_url (str, optional): The GitHub URL for the project. Defaults to "".
            image (str): The Docker image name.
            initial_date (str, optional): The initial release date. Defaults to "".
            name (str): The name of the container image.
            nonroot_supported (bool, optional): Whether the image supports non-root users. Defaults to False.
            ports (list[PortConfig], optional): Ports for the container. Defaults to None.
            project_logo (str, optional): The project logo URL. Defaults to "".
            project_url (str, optional): The project URL. Defaults to "".
            readonly_supported (bool, optional): Whether the image supports read-only filesystems. Defaults to False.
            stable (bool, optional): Whether the image is stable. Defaults to True.
            tags (list[dict[str, str]], optional): Tags for the image. Defaults to None.
            use_common_env_vars (bool, optional): Whether to include common environment variables. Currently PUID and PGID. Defaults to True.
            volumes (list[VolumeConfig], optional): Volumes for the container. Defaults to None.

        Returns:
            ContainerImageConfig: The container image configuration
        """  # noqa: E501
        if tags is None:
            tags = []
        if architectures is None:
            architectures = []
        if volumes is None:
            volumes = []
        if ports is None:
            ports = []
        if env_vars is None:
            env_vars = []
        if devices is None:
            devices = []

        # Apply common env vars if requested
        final_env_vars: list[EnvVarConfig] = env_vars
        if use_common_env_vars:
            final_env_vars = cls.COMMON_ENV_VARS + env_vars

        return cls(
            application_setup=application_setup,
            architectures=architectures,
            category=category,
            deprecated=deprecated,
            description=description,
            devices=devices,
            env_vars=final_env_vars,
            github_url=github_url,
            image=image,
            initial_date=initial_date,
            name=name,
            nonroot_supported=nonroot_supported,
            ports=ports,
            project_logo=project_logo,
            project_url=project_url,
            readonly_supported=readonly_supported,
            stable=stable,
            tags=tags,
            volumes=volumes,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary representation for templates.

        Returns:
            dict: Dictionary representation of the container image configuration.
        """
        return {
            "application_setup": self.application_setup,
            "architectures": self.architectures,
            "category": self.category,
            "deprecated": self.deprecated,
            "description": self.description,
            "devices": [vars(dev) for dev in self.devices],
            "env_vars": [vars(env) for env in self.env_vars],
            "github_url": self.github_url,
            "image": self.image,
            "initial_date": self.initial_date,
            "name": self.name,
            "nonroot_supported": self.nonroot_supported,
            "ports": [vars(port) for port in self.ports],
            "project_logo": self.project_logo,
            "project_url": self.project_url,
            "readonly_supported": self.readonly_supported,
            "stable": self.stable,
            "tags": self.tags,
            "volumes": [vars(vol) for vol in self.volumes],
        }
