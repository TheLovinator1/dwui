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
        name = request.POST.get("name")
        image = request.POST.get("image")

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
                    restart_policy={"Name": "unless-stopped"},
                    ports={"80/tcp": None},  # Auto-assign port
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
