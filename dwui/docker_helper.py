from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import docker

if TYPE_CHECKING:
    import types


logger: logging.Logger = logging.getLogger("dwui")


class DockerClient:
    """A context manager for creating a client for the Docker daemon."""

    def __enter__(self) -> docker.DockerClient:
        """Create a client for the Docker daemon.

        Returns:
            docker.DockerClient: The Docker client.""
        """
        self.client: docker.DockerClient = docker.from_env(use_ssh_client=True, user_agent="dwui")
        return self.client

    def __exit__(self, exc_type: object, exc_value: BaseException | None, traceback: types.TracebackType | None) -> None:
        """Close the client for the Docker daemon.

        Args:
            exc_type (object): The type of the exception.
            exc_value (BaseException | None): The exception object.
            traceback (types.TracebackType | None): The traceback object.
        """
        if exc_value:
            msg = "An error occurred while using the Docker client."
            logger.error(msg, exc_info=(type(exc_value), exc_value, traceback) if exc_value else None)

        self.client.close()
