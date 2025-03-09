from __future__ import annotations

import logging
import socket
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_not_required  # pyright: ignore[reportAttributeAccessIssue]
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from dwui.docker_helper import DockerClient

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger: logging.Logger = logging.getLogger("dwui.views")


@login_not_required
def index(request: HttpRequest) -> HttpResponse:
    """Render the home page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    with DockerClient() as client:
        version: dict = client.version()
        containers = client.containers.list(all=True)

    hostname = socket.gethostname()

    context = {
        "version": version,
        "containers": containers,
        "hostname": hostname,
    }

    return render(request, "index.html", context)


@login_not_required
def new_container(request: HttpRequest) -> HttpResponse:
    """Render the new container form or create a new container.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    # Define a list of popular Linuxserver.io images
    linuxserver_images: list[dict[str, str]] = [
        {"name": "LinuxServer Plex", "image": "linuxserver/plex", "description": "Plex Media Server"},
        {"name": "LinuxServer Nextcloud", "image": "linuxserver/nextcloud", "description": "Personal cloud storage"},
        {"name": "LinuxServer Jellyfin", "image": "linuxserver/jellyfin", "description": "Media server"},
        {"name": "LinuxServer Heimdall", "image": "linuxserver/heimdall", "description": "Application dashboard"},
        {"name": "LinuxServer Calibre-web", "image": "linuxserver/calibre-web", "description": "E-book manager"},
    ]

    if request.method == "POST":
        name: str | None = request.POST.get("name")
        image: str | None = request.POST.get("image")

        if name and image:
            with DockerClient() as client:
                # Pull the image if it doesn't exist
                try:
                    client.images.get(image)
                except Exception:  # noqa: BLE001
                    logger.info("Got the following exception: %s", Exception)
                    client.images.pull(image)

                # Create and start the container
                client.containers.run(
                    image=image,
                    name=name,
                    detach=True,  # Run container in background
                    restart_policy={
                        "Name": "on-failure",
                        "MaximumRetryCount": 5,
                    },
                )

            # Redirect to home page
            return HttpResponseRedirect(reverse("index"))

    context = {
        "linuxserver_images": linuxserver_images,
    }

    return render(request, "new_container.html", context)


@login_not_required
def container_details(request: HttpRequest, container_id: str) -> HttpResponse:
    """Show details for a specific container.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to show details for.

    Returns:
        HttpResponse: The response object containing container details.
    """
    with DockerClient() as client:
        try:
            container = client.containers.get(container_id)
            container_stats = next(container.stats(stream=True, decode=True))
            logs = container.logs(tail=100, timestamps=True).decode("utf-8").splitlines()
        except Exception as e:  # noqa: BLE001
            logger.info("Error retrieving container details: %s", e)
            return HttpResponseRedirect(reverse("index"))

    context = {
        "container": container,
        "container_stats": container_stats,
        "logs": logs,
        "hostname": container.attrs["Config"]["Hostname"],
    }

    return render(request, "container_details.html", context)


@login_not_required
def start_container(request: HttpRequest, container_id: str) -> HttpResponse:
    """Start a Docker container.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to start.

    Returns:
        HttpResponse: Redirect to the container details page.
    """
    with DockerClient() as client:
        try:
            container = client.containers.get(container_id)
            container.start()
            logger.info("Container %s started successfully", container.name)
        except Exception:
            logger.exception("Error starting container %s", container_id)

    return HttpResponseRedirect(reverse("container_details", args=[container_id]))


@login_not_required
def stop_container(request: HttpRequest, container_id: str) -> HttpResponse:
    """Stop a Docker container.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to stop.

    Returns:
        HttpResponse: Redirect to the container details page.
    """
    with DockerClient() as client:
        try:
            container = client.containers.get(container_id)
            container.stop()
            logger.info("Container %s stopped successfully", container.name)
        except Exception:
            logger.exception("Error stopping container %s", container_id)

    return HttpResponseRedirect(reverse("container_details", args=[container_id]))


@login_not_required
def restart_container(request: HttpRequest, container_id: str) -> HttpResponse:
    """Restart a Docker container.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to restart.

    Returns:
        HttpResponse: Redirect to the container details page.
    """
    with DockerClient() as client:
        try:
            container = client.containers.get(container_id)
            container.restart()
            logger.info("Container %s restarted successfully", container.name)
        except Exception:
            logger.exception("Error restarting container %s", container_id)

    return HttpResponseRedirect(reverse("container_details", args=[container_id]))


@login_not_required
def remove_container(request: HttpRequest, container_id: str) -> HttpResponse:
    """Remove a Docker container.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to remove.

    Returns:
        HttpResponse: Redirect to the home page.
    """
    with DockerClient() as client:
        try:
            container = client.containers.get(container_id)
            container_name = container.name
            container.remove(force=True)  # Force removal even if running
            logger.info("Container %s removed successfully", container_name)
        except Exception:
            logger.exception("Error removing container %s", container_id)

    return HttpResponseRedirect(reverse("index"))


@login_not_required
def update_container(request: HttpRequest, container_id: str) -> HttpResponse:
    """Update a Docker container by recreating it with the latest image.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to update.

    Returns:
        HttpResponse: Redirect to the home page.
    """
    with DockerClient() as client:
        try:
            # Get container details
            container = client.containers.get(container_id)
            name = container.name
            image_name = ""
            if container.image:
                image_name = container.image.tags[0] if container.image.tags else container.image.id or ""
            ports = container.attrs["HostConfig"]["PortBindings"]
            volumes = container.attrs["HostConfig"]["Binds"]
            env_vars = container.attrs["Config"]["Env"]
            restart_policy = container.attrs["HostConfig"]["RestartPolicy"]

            # Pull latest image
            logger.info("Pulling latest image for %s", image_name)
            client.images.pull(image_name.split(":")[0])

            # Stop and remove existing container
            logger.info("Stopping and removing container %s", name)
            container.stop()
            container.remove()

            # Create and start new container with same parameters
            logger.info("Creating new container %s with updated image", name)
            new_container = client.containers.run(
                image=image_name,
                name=name,
                detach=True,
                ports=dict(ports.items()),
                volumes={volume.split(":")[0]: {"bind": volume.split(":")[1], "mode": "rw"} for volume in volumes},
                environment=env_vars,
                restart_policy=restart_policy,
            )

            logger.info("Container %s updated successfully with ID %s", name, new_container.id)
            return HttpResponseRedirect(reverse("container_details", args=[new_container.id]))

        except Exception as e:  # noqa: BLE001
            logger.info("Error updating container %s: %s", container_id, e)
            return HttpResponseRedirect(reverse("index"))
