from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import requests
from django.contrib.auth.decorators import login_not_required  # pyright: ignore[reportAttributeAccessIssue]
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from packaging import version

from dwui.api_client import APIClient
from dwui.container_images import get_categories, get_container_image_by_name, get_container_images

if TYPE_CHECKING:
    from django.http import HttpRequest

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
def get_containers(request: HttpRequest) -> HttpResponse:
    """Handle htmx request for getting containers.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response containing the containers list.
    """
    api_client = APIClient()
    containers: dict[str, Any] = api_client.get_all_containers()
    if not containers:
        logger.warning("No containers found.")
        context: dict[str, Any] = {"containers": []}
    else:
        context: dict[str, Any] = {"containers": containers}

    logger.info("Number of containers found: %d", len(containers))

    return render(request, "partials/containers_list.html", context)


@login_not_required
def index(request: HttpRequest) -> HttpResponse:
    """Render the home page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    api_client = APIClient()
    current_version_info: dict = api_client.get_docker_version()

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
        "is_outdated": is_outdated,
        "latest_version": latest_version,
        "version_message": version_message,
        "version": current_version_info,
    }

    return render(request, "index.html", context)


def create_container(request: HttpRequest, name: str, image: str) -> HttpResponse:
    """Create a new Docker container with the provided configurations.

    Args:
        request (HttpRequest): The request object.
        name (str): The name of the container.
        image (str): The Docker image to use.

    Returns:
        HttpResponse: Redirect to the container details page.
    """
    binds: str = request.POST.get("binds", "")
    ports: str = request.POST.get("ports", "")
    env_vars: str = request.POST.get("env_vars", "")
    restart_policy: str = request.POST.get("restart_policy", "always")

    api_client = APIClient()
    container: dict[str, Any] = api_client.create_container(
        image=image,
        name=name,
        ports=ports,
        binds=binds,
        env_vars=env_vars,
        restart_policy=restart_policy,
    )
    logger.info("Container %s created successfully with ID %s", name, container["id"])
    return HttpResponseRedirect(reverse("container_details", args=[container["id"]]))


@login_not_required
def new_container(request: HttpRequest) -> HttpResponse:
    """Render the new container form or create a new container.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    # Get container images from the container_images module
    container_images: list[dict] = get_container_images()
    categories: list[str] = get_categories()

    if request.method == "POST":
        logger.info("Form submitted with POST method. %s", request.POST)
        name: str | None = request.POST.get("name")
        image: str | None = request.POST.get("image")

        if name and image:
            logger.info("Creating container with name: %s, image: %s", name, image)
            return create_container(request, name, image)

    context: dict[str, Any] = {"container_images": container_images, "categories": categories}

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
    api_client = APIClient()
    container = api_client.get_container_details(container_id)

    context = {
        "container": container,
        # "container_stats": container_stats,
        # "logs": logs,
        # "hostname": container.attrs["Config"]["Hostname"],
        # "container_metadata": container_metadata,
    }

    return render(request, "container_details.html", context)


"""
@login_not_required
def start_container(request: HttpRequest, container_id: str) -> HttpResponse:
    Start a Docker container.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to start.

    Returns:
        HttpResponse: Redirect to the container details page.

    with DockerClient() as client:
        try:
            container = client.containers.get(container_id)
            container.start()
            logger.info("Container %s started successfully", container.name)
        except Exception:
            logger.exception("Error starting container %s", container_id)

    return HttpResponseRedirect(reverse("container_details", args=[container_id]))
"""

"""
@login_not_required
def stop_container(request: HttpRequest, container_id: str) -> HttpResponse:
    Stop a Docker container.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to stop.

    Returns:
        HttpResponse: Redirect to the container details page.

    with DockerClient() as client:
        try:
            container = client.containers.get(container_id)
            container.stop()
            logger.info("Container %s stopped successfully", container.name)
        except Exception:
            logger.exception("Error stopping container %s", container_id)

    return HttpResponseRedirect(reverse("container_details", args=[container_id]))
"""

"""
@login_not_required
def restart_container(request: HttpRequest, container_id: str) -> HttpResponse:
    Restart a Docker container.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to restart.

    Returns:
        HttpResponse: Redirect to the container details page.

    with DockerClient() as client:
        try:
            container = client.containers.get(container_id)
            container.restart()
            logger.info("Container %s restarted successfully", container.name)
        except Exception:
            logger.exception("Error restarting container %s", container_id)

    return HttpResponseRedirect(reverse("container_details", args=[container_id]))
"""

"""
@login_not_required
def remove_container(request: HttpRequest, container_id: str) -> HttpResponse:
    Remove a Docker container.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to remove.

    Returns:
        HttpResponse: Redirect to the home page.

    with DockerClient() as client:
        try:
            container = client.containers.get(container_id)
            container_name = container.name
            container.remove(force=True)  # Force removal even if running
            logger.info("Container %s removed successfully", container_name)
        except Exception:
            logger.exception("Error removing container %s", container_id)

    return HttpResponseRedirect(reverse("index"))
"""

"""
@login_not_required
def update_container(request: HttpRequest, container_id: str) -> HttpResponse:
    Update a Docker container by recreating it with the latest image.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to update.

    Returns:
        HttpResponse: Redirect to the home page.

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
"""


@login_not_required
def image_config(request: HttpRequest) -> HttpResponse:
    """Handle htmx request for container image configuration.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response containing the configuration form.
    """
    image_name: str = request.GET.get("image", "")
    display_name: str = request.GET.get("display_name", "")

    # Get container image configuration
    image_config_dict: dict | None = get_container_image_by_name(image_name)

    if not image_config_dict:
        # Handle case when image is not found
        return HttpResponse("Image configuration not found", status=404)

    # Create a suggested name based on the image display name
    suggested_name: str = display_name.lower().replace(" ", "-").replace("/", "-")
    suggested_name = "".join(c for c in suggested_name if c.isalnum() or c == "-")

    # Get all available networks

    context: dict[str, Any] = {
        "image_config": image_config_dict,
        "image_name": image_name,
        "image_display_name": display_name,
        "suggested_name": suggested_name,
        "networks": "",
    }

    return render(request, "partials/container_config_form.html", context)
