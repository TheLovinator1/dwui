from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, Self

import httpx
from fabric import Connection

if TYPE_CHECKING:
    import types

    import paramiko

logger: logging.Logger = logging.getLogger("dwui")


class DockerAPIError(Exception):
    """Base exception for Docker API errors."""


class DockerConnectionError(DockerAPIError):
    """Exception for connection errors."""


class DockerImageNotFoundError(DockerAPIError):
    """Exception for Docker image not found."""


@dataclass
class Container:
    """Docker container."""

    name: str
    id: str
    status: str


class Client:
    """Client for interacting with Docker API over SSH and local Unix socket."""

    def __init__(self) -> None:
        """Initialize the client."""
        self.ssh_client: paramiko.SSHClient | None = None
        self.http_client = httpx.Client()

    def __enter__(self) -> Self:
        """Enter the runtime context related to this object.

        Returns:
            The object itself.
        """
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None) -> None:
        """Exit the runtime context related to this object."""
        self.close()

    @staticmethod
    def execute_command(command: str) -> str:
        """Execute a Docker API command.

        Args:
            command: Command to execute

        Raises:
            DockerAPIError: If the command execution fails.

        Returns:
            Response from the command.
        """
        host: str | None = os.environ.get("DOCKER_HOST")
        c = Connection(host=host)
        result = c.run(command)
        response_str = result.stdout.strip()
        logger.info("Executed command: '%s', actual command: '%s'", command, result.command)
        logger.info("Response: '%s'", response_str)

        if not result.ok:
            msg: str = f"Command '{command}' failed. Output: '{result.stderr.strip()}'"
            raise DockerAPIError(msg)

        return response_str

    def get_containers_name_id_and_status(self) -> list[Container]:
        """Get a list of Docker containers with their names, IDs, and running status.

        Returns:
            List of Docker containers with their names, IDs, and running status
        """
        response: str = self.execute_command('docker ps --format "{{.Names}},{{.ID}},{{.State}}"')
        return [Container(name=line.split(",")[0], id=line.split(",")[1], status=line.split(",")[2]) for line in response.splitlines()]

    def get_volumes(self) -> list[dict[str, Any]]:
        """Get a list of Docker volumes.

        Returns:
            List of Docker volumes.
        """
        response: str = self.execute_command('docker volume ls --format "{{json .}}"')
        return [json.loads(line) for line in response.splitlines()]

    def get_networks(self) -> list[dict[str, Any]]:
        """Get a list of Docker networks.

        Returns:
            List of Docker networks.
        """
        response: str = self.execute_command('docker network ls --format "{{json .}}"')
        return [json.loads(line) for line in response.splitlines()]

    def get_version(self) -> dict[str, Any]:
        """Get the Docker version.

        Returns:
            Docker version.
        """
        response: str = self.execute_command('docker version --format "{{json .}}"')
        return json.loads(response)

    def get_images(self) -> list[dict[str, Any]]:
        """Get a list of Docker images.

        Returns:
            List of Docker images.
        """
        response: str = self.execute_command('docker image ls --format "{{json .}}"')
        return [json.loads(line) for line in response.splitlines()]

    def get_image_by_name(self, name: str) -> dict[str, Any]:
        """Get details of a specific Docker image by name.

        Args:
            name: The name of the Docker image.

        Raises:
            DockerAPIError: If the image is not found.
            DockerImageNotFoundError: If the image is not found.

        Returns:
            Details of the Docker image.
        """
        response: str = self.execute_command(f'docker image inspect {name} --format "{{json .}}"')
        if not response:
            msg: str = f"Image '{name}' not found."
            raise DockerAPIError(msg)

        if response.startswith("Error response from daemon: No such image:"):
            msg: str = f"Image '{name}' not found."
            raise DockerImageNotFoundError(msg)

        return json.loads(response)

    def pull_image(self, name: str) -> None:
        """Pull a Docker image.

        Args:
            name: The name of the Docker image.
        """
        self.execute_command(f"docker image pull {name}")

    def run_container(
        self,
        image: str,
        name: str,
        ports: dict,
        volumes: list,
        environment: list,
        restart_policy: Literal["always", "on-failure", "unless-stopped", "no"] = "unless-stopped",
    ) -> None:
        """Run a Docker container with the specified configurations.

        Args:
            image: The name of the Docker image.
            name: The name of the Docker container.
            ports: Port mappings for the container. Format: {"host_port": "container_port"}.
            volumes: Volume bindings for the container.
            environment: Environment variables for the container.
            restart_policy: Restart policy for the container.
        """
        command: str = (
            f"docker run --name {name} -d "
            f"{' '.join(f'-p {host_port}:{container_port}' for host_port, container_port in ports.items())} "
            f"{' '.join(f'-v {volume}' for volume in volumes)} "
            f"{' '.join(f'-e {env}' for env in environment)} {image} "
            f"--restart {restart_policy}"
        )
        self.execute_command(command)

    def get_container_id_by_name(self, name: str) -> str:
        """Get the ID of a Docker container by name.

        Args:
            name: The name of the Docker container.

        Returns:
            The ID of the Docker container.
        """
        response: str = self.execute_command(f'docker ps -qf "name={name}"')
        return response.strip()

    def start_container(self, name: str) -> None:
        """Start a Docker container.

        Args:
            name: The name of the Docker container.
        """
        container_id: str = self.get_container_id_by_name(name)
        self.execute_command(f"docker start {container_id}")

    def stop_container(self, name: str) -> None:
        """Stop a Docker container.

        Args:
            name: The name of the Docker container.
        """
        container_id: str = self.get_container_id_by_name(name)
        self.execute_command(f"docker stop {container_id}")

    def restart_container(self, name: str) -> None:
        """Restart a Docker container.

        Args:
            name: The name of the Docker container.
        """
        container_id: str = self.get_container_id_by_name(name)
        self.execute_command(f"docker restart {container_id}")
        logger.info("Container %s restarted successfully", name)

    def remove_container(self, name: str) -> None:
        """Remove a Docker container.

        Args:
            name: The name of the Docker container.
        """
        container_id: str = self.get_container_id_by_name(name)
        self.stop_container(name)
        self.execute_command(f"docker rm {container_id}")
        logger.info("Container %s removed successfully", name)

    def close(self) -> None:
        """Close all connections."""
        if self.ssh_client:
            self.ssh_client.close()

        if self.http_client:
            self.http_client.close()
        logger.info("Closed all connections.")
