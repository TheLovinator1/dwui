"""This Django application serves as the agent for the DWUI project.

It provides a simple HTTP interface for the agent to communicate with the DWUI server.
It is designed to be run as a Docker container; you need to mount /var/run/docker.sock
to the container to allow it to communicate with the Docker daemon.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import TYPE_CHECKING, Any

import django
import docker
from django.core.handlers.wsgi import WSGIHandler
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import path
from docker import errors

from agent.parsers import get_binds, get_env_vars, get_ports, get_restart_policy

if TYPE_CHECKING:
    import types

    from django.urls.resolvers import URLPattern
    from docker.models.containers import Container

logger: logging.Logger = logging.getLogger("dwui.agent")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()


class DockerClient:
    """A context manager for creating a client for the Docker daemon."""

    # TODO(TheLovinator): There is a max_pool_size parameter in from_env(); does that mean we don't need to use DockerClient as a context manager?  # noqa: TD003

    def __enter__(self) -> docker.DockerClient:
        """Create a client for the Docker daemon.

        Returns:
            docker.DockerClient: The Docker client.""
        """
        self.client: docker.DockerClient = docker.from_env()
        logger.info("Docker client created.")
        logger.debug("Docker client: %s", self.client)
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

        logger.info("Closing Docker client.")
        if hasattr(self, "client") and isinstance(self.client, docker.DockerClient):
            logger.debug("Docker client: %s", self.client)

        self.client.close()


# /
def index(request: HttpRequest) -> HttpResponse:
    """Index view for the agent.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    formatted_docker_version: str = ""
    with DockerClient() as client:
        docker_version: str = client.version()
        formatted_docker_version: str = json.dumps(docker_version, indent=4)

    return HttpResponse(f"Hello, world!\n<pre>{formatted_docker_version}</pre>\n\n")


# /robots.txt
def robots_txt(request: HttpRequest) -> HttpResponse:
    """Robots.txt view for the agent.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object with directives to prevent crawling and indexing.
    """
    content = "User-agent: *\nDisallow: /\nNoindex: /\n"
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


# /health/ or /healthz
def health_check(request: HttpRequest) -> HttpResponse:
    """Health check view for the agent.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    return HttpResponse("OK")


# /api/v1/containers/
def list_all_containers(request: HttpRequest) -> HttpResponse:
    """List all containers view for the agent.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object with a list of all containers.
    """
    with DockerClient() as client:
        try:
            containers: list[Container] = client.containers.list(all=True)
        except errors.APIError as e:
            logger.exception("Error listing containers. Request: %s", request)
            return HttpResponse(f"Error listing containers:\n{e}", status=500)

        logger.debug("Containers: %s", containers)

        container_list = [container.name for container in containers]
        return JsonResponse(container_list, safe=False, json_dumps_params={"indent": 4})


# /api/v1/containers/<container_id>/
def get_container_details(request: HttpRequest, container_id: str) -> HttpResponse:
    """Get container details view for the agent.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container.

    Returns:
        HttpResponse: The response object with the container details.
    """
    with DockerClient() as client:
        try:
            container: Container = client.containers.get(container_id)
        except errors.NotFound as e:
            logger.exception("Container not found. Request: %s", request)
            return HttpResponse(f"Container not found:\n{e}", status=404)
        except errors.APIError as e:
            logger.exception("Error retrieving container. Request: %s", request)
            return HttpResponse(f"Error retrieving container:\n{e}", status=500)

        container_data: dict[str, Any] = {
            "id": container.id,
            "name": container.name,
            "status": container.status,
            "created": container.attrs["Created"],
            "ports": container.ports,
        }

        return JsonResponse(container_data, safe=False, json_dumps_params={"indent": 4})


# /api/v1/containers/create/
def create_container(request: HttpRequest) -> HttpResponse:
    """Create a container view for the agent.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object with the created container details.
    """
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    image: str = request.POST.get("image", "")
    name: str = request.POST.get("name", "")
    ports: str = request.POST.get("ports", "")
    binds: str = request.POST.get("binds", "")
    env_vars: str = request.POST.get("env_vars", "")
    restart_policy: str = request.POST.get("restart_policy", "always")

    logger.info("Trying to create container with the following parameters:")
    for key, value in request.POST.items():
        logger.info("%s: %s", key, value)

    # TODO(TheLovinator): Validate the input parameters  # noqa: TD003
    # TODO(TheLovinator): Use an allowlist for the image names  # noqa: TD003

    with DockerClient() as client:
        try:
            client.images.get(image)
        except errors.ImageNotFound:
            logger.info("Pulling image %s", image)
            client.images.pull(image)
        except errors.APIError:
            logger.exception("Error pulling image %s", image)
            return HttpResponse(f"Error pulling image {image}", status=500)

        try:
            container: Container = client.containers.create(
                image=image,
                name=name,
                detach=True,
                ports=get_ports(ports),
                volumes=get_binds(binds),
                environment=get_env_vars(env_vars) if env_vars else None,
                restart_policy=get_restart_policy(restart_policy),
            )
            logger.info("Container created: %s", container)

            container_data: dict[str, Any] = {
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "created": container.attrs["Created"],
                "ports": container.ports,
            }

            logger.debug("Container data: %s", container_data)

            return JsonResponse(container_data, safe=False, json_dumps_params={"indent": 4})
        except errors.APIError as e:
            logger.exception("Error creating container. Request: %s", request)
            return HttpResponse(f"Error creating container:\n{e}", status=500)


def get_docker_version(request: HttpRequest) -> HttpResponse:
    """Get the Docker version.

    Returns:
        str: The Docker version.
    """
    with DockerClient() as client:
        try:
            version: str = client.version()
            logger.info("Docker version: %s", version)
        except errors.APIError as e:
            logger.exception("Error retrieving Docker version.")
            return HttpResponse(f"Error retrieving Docker version:\n{e}", status=500)
        else:
            return JsonResponse(
                version,
                safe=False,
                json_dumps_params={"indent": 4},
            )


urlpatterns: list[URLPattern] = [
    # /
    path("", index, name="index"),
    # /health/ or /healthz
    path("health/", health_check, name="health_check"),
    path("healthz/", health_check, name="health_check"),
    # /robots.txt
    path("robots.txt", robots_txt, name="robots_txt"),
    # /api/v1/containers/
    path("api/v1/containers/", list_all_containers, name="list_all_containers"),
    # /api/v1/containers/<container_id>/
    path("api/v1/containers/<str:container_id>/", get_container_details, name="get_container_details"),
    # /api/v1/containers/create/
    path("api/v1/containers/create/", create_container, name="create_container"),
    # /api/v1/docker/version/
    path("api/v1/docker/version/", get_docker_version, name="get_docker_version"),
]

application: WSGIHandler = WSGIHandler()

if __name__ == "__main__":
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        msg = (
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
        raise ImportError(msg) from exc
    execute_from_command_line(sys.argv)
