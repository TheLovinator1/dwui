from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import requests
from django.contrib.auth.decorators import login_not_required  # pyright: ignore[reportAttributeAccessIssue]
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from docker import errors
from packaging import version

from dwui.docker_helper import DockerClient

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger: logging.Logger = logging.getLogger("dwui.views")


def get_latest_docker_version() -> str | None:
    """Get the latest Docker version from Arch Linux package repository.

    Returns:
        str | None: The latest version string or None if unable to fetch.
    """
    try:
        response: requests.Response = requests.get("https://archlinux.org/packages/extra/x86_64/docker/json/", timeout=5)
        response.raise_for_status()
        data: dict[str, Any] = response.json()

        # Extract the version from the JSON data
        latest_version: str = data.get("pkgver", "")
        if latest_version:
            return latest_version
    except Exception:
        logger.exception("Failed to fetch latest Docker version")
    return None


@login_not_required
def index(request: HttpRequest) -> HttpResponse:
    """Render the home page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    with DockerClient() as client:
        current_version_info: dict = client.version()
        containers: list = client.containers.list(all=True)

    current_version: str = current_version_info.get("Version", "")
    latest_version: str | None = get_latest_docker_version()
    is_outdated = False
    version_message: str | None = None
    changelog_url: str = "https://docs.docker.com/engine/release-notes/"

    if latest_version and current_version:
        try:
            # Remove any leading 'v' prefix if present
            latest_version = latest_version.removeprefix("v")
            current_version = current_version.removeprefix("v")

            logger.info("Current Docker version: %s, Latest version: %s", current_version, latest_version)

            # Compare versions
            is_outdated: bool = version.parse(current_version) < version.parse(latest_version)
            if is_outdated:
                version_message = f"Your Docker version ({current_version}) is outdated. Latest version is {latest_version}."
        except Exception:
            logger.exception("Error comparing Docker versions")

    context: dict[str, Any] = {
        "changelog_url": changelog_url,
        "containers": containers,
        "is_outdated": is_outdated,
        "latest_version": latest_version,
        "version_message": version_message,
        "version": current_version_info,
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
                except errors.ImageNotFound:
                    logger.info("Pulling image %s", image)
                    client.images.pull(image)
                except errors.APIError:
                    logger.exception("Error pulling image %s", image)
                    return HttpResponseRedirect(reverse("index"))

                # Create and start the container
                container = client.containers.run(
                    image=image,
                    name=name,
                    detach=True,  # Run container in background
                    restart_policy={
                        "Name": "on-failure",
                        "MaximumRetryCount": 5,
                    },
                )

                logger.info("Container %s created successfully with ID %s", name, container.id)
                return HttpResponseRedirect(reverse("container_details", args=[container.id]))

    context: dict[str, list[dict[str, str]]] = {
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
