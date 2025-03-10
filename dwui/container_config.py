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

    def __post_init__(self) -> None:
        """Validate the volume configuration.

        Raises:
            ValueError: If the target or description is missing.
        """
        if not self.target:
            msg = "Volume target path is required"
            raise ValueError(msg)
        if not self.description:
            msg = "Volume description is required"
            raise ValueError(msg)


@dataclass
class PortConfig:
    """Class for port configuration."""

    container: str
    description: str
    protocol: Literal["tcp", "udp"] = "tcp"
    host: str = ""

    def __post_init__(self) -> None:
        """Validate the port configuration.

        Raises:
            ValueError: If the container port, description, or protocol is invalid.
        """
        if not self.container:
            msg = "Container port is required"
            raise ValueError(msg)
        if not self.description:
            msg = "Port description is required"
            raise ValueError(msg)
        if self.protocol not in {"tcp", "udp"}:
            msg = f"Invalid protocol: {self.protocol}, must be 'tcp' or 'udp'"
            raise ValueError(msg)


@dataclass
class EnvVarConfig:
    """Class for environment variable configuration."""

    name: str
    description: str
    required: bool = False
    default: str | None = None
    options: list[str] | None = None

    def __post_init__(self) -> None:
        """Validate the environment variable configuration.

        Raises:
            ValueError: If the environment variable name or description is missing,
                        or if the default value is not in the options list.
        """
        if not self.name:
            msg = "Environment variable name is required"
            raise ValueError(msg)
        if not self.description:
            msg = "Environment variable description is required"
            raise ValueError(msg)
        if self.options and self.default and self.default not in self.options:
            msg = f"Default value '{self.default}' not in options: {self.options}"
            raise ValueError(msg)


@dataclass
class ContainerImageConfig:
    """Class for container image configuration."""

    name: str
    image: str
    description: str
    category: str

    # Additional fields
    initial_date: str = ""
    github_url: str = ""
    project_url: str = ""
    project_logo: str = ""
    version: str = ""
    version_timestamp: str = ""
    stable: bool = True
    deprecated: bool = False
    stars: int = 0
    monthly_pulls: int = 0
    tags: list[dict[str, str]] = field(default_factory=list)
    architectures: list[dict[str, str]] = field(default_factory=list)
    changelog: list[dict[str, str]] = field(default_factory=list)

    # Container configuration
    volumes: list[VolumeConfig] = field(default_factory=list)
    ports: list[PortConfig] = field(default_factory=list)
    env_vars: list[EnvVarConfig] = field(default_factory=list)

    COMMON_ENV_VARS: ClassVar[list[EnvVarConfig]] = [
        EnvVarConfig(name="PUID", default="1000", description="User ID", required=True),
        EnvVarConfig(name="PGID", default="1000", description="Group ID", required=True),
    ]

    def __post_init__(self) -> None:
        """Validate the container image configuration.

        Raises:
            ValueError: If any required field is missing.
        """
        if not self.name:
            msg = "Container image name is required"
            raise ValueError(msg)
        if not self.image:
            msg = "Docker image name is required"
            raise ValueError(msg)
        if not self.description:
            msg = "Container image description is required"
            raise ValueError(msg)
        if not self.category:
            msg = "Container image category is required"
            raise ValueError(msg)

    @classmethod
    def with_common_env_vars(
        cls,
        name: str,
        image: str,
        description: str,
        category: str,
        volumes: list[VolumeConfig] | None = None,
        ports: list[PortConfig] | None = None,
        env_vars: list[EnvVarConfig] | None = None,
    ) -> ContainerImageConfig:
        """Create a container image config with common environment variables.

        Returns:
            ContainerImageConfig: The container image configuration with common environment variables.
        """
        if volumes is None:
            volumes = []
        if ports is None:
            ports = []
        if env_vars is None:
            env_vars = []

        return cls(
            name=name,
            image=image,
            description=description,
            category=category,
            volumes=volumes,
            ports=ports,
            env_vars=cls.COMMON_ENV_VARS + env_vars,
        )

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
        project_logo: str = "",
        version: str = "",
        version_timestamp: str = "",
        stars: int = 0,
        monthly_pulls: int = 0,
        tags: list[dict[str, str]] | None = None,
        architectures: list[dict[str, str]] | None = None,
        changelog: list[dict[str, str]] | None = None,
        volumes: list[VolumeConfig] | None = None,
        ports: list[PortConfig] | None = None,
        env_vars: list[EnvVarConfig] | None = None,
        *,
        use_common_env_vars: bool = True,
        stable: bool = True,
        deprecated: bool = False,
    ) -> ContainerImageConfig:
        """Create a complete container image configuration with all available fields.

        Args:
            name (str): The name of the container image.
            image (str): The Docker image name.
            description (str): The description of the container image.
            category (str): The category of the container image.
            initial_date (str, optional): The initial release date. Defaults to "".
            github_url (str, optional): The GitHub URL for the project. Defaults to "".
            project_url (str, optional): The project URL. Defaults to "".
            project_logo (str, optional): The project logo URL. Defaults to "".
            version (str, optional): The version of the container image. Defaults to "".
            version_timestamp (str, optional): The timestamp of the version. Defaults to "".
            stable (bool, optional): Whether the image is stable. Defaults to True.
            deprecated (bool, optional): Whether the image is deprecated. Defaults to False.
            stars (int, optional): The number of stars for the project. Defaults to 0.
            monthly_pulls (int, optional): The number of monthly pulls. Defaults to 0.
            tags (list[dict[str, str]], optional): Tags for the image. Defaults to None.
            architectures (list[dict[str, str]], optional): Supported architectures. Defaults to None.
            changelog (list[dict[str, str]], optional): Changelog for the image. Defaults to None.
            volumes (list[VolumeConfig], optional): Volumes for the container. Defaults to None.
            ports (list[PortConfig], optional): Ports for the container. Defaults to None.
            env_vars (list[EnvVarConfig], optional): Environment variables for the container. Defaults to None.
            use_common_env_vars (bool, optional): Whether to include common environment variables. Defaults to True.

        Returns:
            ContainerImageConfig: The container image configuration
        """
        if tags is None:
            tags = []
        if architectures is None:
            architectures = []
        if changelog is None:
            changelog = []
        if volumes is None:
            volumes = []
        if ports is None:
            ports = []
        if env_vars is None:
            env_vars = []

        # Apply common env vars if requested
        final_env_vars = env_vars
        if use_common_env_vars:
            final_env_vars = cls.COMMON_ENV_VARS + env_vars

        return cls(
            name=name,
            image=image,
            description=description,
            category=category,
            initial_date=initial_date,
            github_url=github_url,
            project_url=project_url,
            project_logo=project_logo,
            version=version,
            version_timestamp=version_timestamp,
            stable=stable,
            deprecated=deprecated,
            stars=stars,
            monthly_pulls=monthly_pulls,
            tags=tags,
            architectures=architectures,
            changelog=changelog,
            volumes=volumes,
            ports=ports,
            env_vars=final_env_vars,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary representation for templates.

        Returns:
            dict: Dictionary representation of the container image configuration.
        """
        return {
            "name": self.name,
            "image": self.image,
            "description": self.description,
            "category": self.category,
            "initial_date": self.initial_date,
            "github_url": self.github_url,
            "project_url": self.project_url,
            "project_logo": self.project_logo,
            "version": self.version,
            "version_timestamp": self.version_timestamp,
            "stable": self.stable,
            "deprecated": self.deprecated,
            "stars": self.stars,
            "monthly_pulls": self.monthly_pulls,
            "tags": self.tags,
            "architectures": self.architectures,
            "changelog": self.changelog,
            "volumes": [vars(vol) for vol in self.volumes],
            "ports": [vars(port) for port in self.ports],
            "env_vars": [vars(env) for env in self.env_vars],
        }
