from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import requests
from django.contrib.auth.decorators import login_not_required  # pyright: ignore[reportAttributeAccessIssue]
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from packaging import version

from dwui.container_images import get_categories, get_container_image_by_name, get_container_images
from dwui.docker_helper import Client, DockerAPIError, DockerImageNotFoundError

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
    with Client() as client:
        containers = client.get_containers_name_id_and_status()

    context: dict[str, Any] = {"containers": containers}
    return render(request, "partials/containers_list.html", context)


@login_not_required
def index(request: HttpRequest) -> HttpResponse:
    """Render the home page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    with Client() as client:
        current_version_info: dict = client.get_version()

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


def create_container(request: HttpRequest, name: str, image: str) -> HttpResponse:  # noqa: C901, PLR0912
    """Create a new Docker container with the provided configurations.

    Args:
        request (HttpRequest): The request object.
        name (str): The name of the container.
        image (str): The Docker image to use.

    Returns:
        HttpResponse: Redirect to the container details page.
    """
    with Client() as client:
        # Pull the image if it doesn't exist
        try:
            client.get_image_by_name(image)
        except DockerImageNotFoundError:
            logger.info("Pulling image %s", image)
            client.pull_image(image)
        except DockerAPIError:
            logger.exception("Error pulling image %s", image)
            return HttpResponseRedirect(reverse("index"))

        # Process volumes from form
        volume_data = {}
        for key, value in request.POST.items():
            if key.startswith("volume_"):
                parts = key.split("_", 2)
                if len(parts) == 3:  # noqa: PLR2004
                    volume_id = parts[1]
                    field = parts[2]
                    if volume_id not in volume_data:
                        volume_data[volume_id] = {}
                    volume_data[volume_id][field] = value

        # Format volumes for Docker
        binds: list[str] = [
            f"{vol['source']}:{vol['target']}"
            for vol in volume_data.values()
            if "source" in vol and "target" in vol and vol["source"].strip()
        ]

        # Process ports from form
        ports = {}
        for key, value in request.POST.items():
            if key.startswith("port_") and value.strip():
                parts = key.split("_", 3)
                if len(parts) == 4 and parts[2] == "host":  # noqa: PLR2004
                    port_id = parts[1]
                    container_port = request.POST.get(f"port_{port_id}_container")
                    protocol = request.POST.get(f"port_{port_id}_protocol", "tcp")
                    if container_port:
                        ports[f"{container_port}/{protocol}"] = value

        # Process environment variables from form
        env_vars = []
        for key, value in request.POST.items():
            if key.startswith("env_") and value.strip():
                parts = key.split("_", 2)
                if len(parts) == 3:  # noqa: PLR2004
                    env_name = parts[2]
                    env_vars.append(f"{env_name}={value}")

        restart_policy_str: str = request.POST.get("restart_policy", "on-failure")
        allowed_policies = ("always", "on-failure", "unless-stopped", "no")

        if restart_policy_str in allowed_policies:
            restart_policy = restart_policy_str
        else:
            logger.warning("Invalid restart policy: %s. Using default: on-failure", restart_policy_str)
            restart_policy = "on-failure"  # Default

        client.run_container(
            image=image,
            name=name,
            ports=ports,
            volumes=binds,
            environment=env_vars,
            restart_policy=restart_policy,
        )

        # Get the container ID
        container_id: str = client.get_container_id_by_name(name)

        logger.info("Container %s created successfully with ID %s", name, container_id)
        return HttpResponseRedirect(reverse("container_details", args=[container_id]))


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
    with Client() as client:
        try:
            container: str = client.get_container_id_by_name(container_id)
        except Exception as e:  # noqa: BLE001
            logger.info("Error retrieving container details: %s", e)
            return HttpResponseRedirect(reverse("index"))

    context = {
        "container": container,
        "container_stats": None,
        "logs": None,
        "hostname": None,
        "container_metadata": None,
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
    with Client() as client:
        try:
            client.start_container(container_id)
            logger.info("Container %s started successfully", container_id)
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
    with Client() as client:
        try:
            client.stop_container(container_id)
            logger.info("Container %s stopped successfully", container_id)
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
    with Client() as client:
        try:
            client.restart_container(container_id)
            logger.info("Container %s restarted successfully", container_id)
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
    with Client() as client:
        try:
            client.remove_container(container_id)
            logger.info("Container %s removed successfully", container_id)
        except Exception:
            logger.exception("Error removing container %s", container_id)

    return HttpResponseRedirect(reverse("index"))


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
    with Client() as client:
        networks = client.get_networks()

    context: dict[str, Any] = {
        "image_config": image_config_dict,
        "image_name": image_name,
        "image_display_name": display_name,
        "suggested_name": suggested_name,
        "networks": networks,
    }

    return render(request, "partials/container_config_form.html", context)
