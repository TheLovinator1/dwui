from __future__ import annotations

import os

import docker


def test_if_docker_is_installed_in_ci() -> None:
    """Test if Docker is installed in the CI environment."""
    if os.getenv("CI"):
        client: docker.DockerClient = docker.from_env()
        assert client.ping() is True, "Docker is not installed in the CI environment"
        client.close()
