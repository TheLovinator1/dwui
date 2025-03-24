from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, Literal, cast

import requests
from django.contrib.auth.decorators import login_not_required  # pyright: ignore[reportAttributeAccessIssue]
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html
from docker import errors
from packaging import version

from dwui.console import remove_ansi
from dwui.container_images import get_categories, get_container_image_by_name, get_container_images
from dwui.docker_helper import DockerClient

if TYPE_CHECKING:
    from datetime import datetime

    from django.http import HttpRequest
    from docker.models.containers import Container, _RestartPolicy

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
    with DockerClient() as client:
        containers: dict[str, Any] = client.containers.list(all=True)
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
    with DockerClient() as client:
        current_version_info: dict = client.version()

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

        # Process volumes from form
        volume_data = {}
        for key, value in request.POST.items():
            if key.startswith("volume_"):
                parts = key.split("_", 2)
                if len(parts) == 3:
                    volume_id = parts[1]
                    field = parts[2]
                    if volume_id not in volume_data:
                        volume_data[volume_id] = {}
                    volume_data[volume_id][field] = value

        # Format volumes for Docker
        binds = [
            f"{vol['source']}:{vol['target']}"
            for vol in volume_data.values()
            if "source" in vol and "target" in vol and vol["source"].strip()
        ]

        # Process ports from form
        ports = {}
        for key, value in request.POST.items():
            if key.startswith("port_") and value.strip():
                parts = key.split("_", 3)
                if len(parts) == 4 and parts[2] == "host":
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
                if len(parts) == 3:
                    env_name = parts[2]
                    env_vars.append(f"{env_name}={value}")

        max_retries = int(request.POST.get("max_retry_count", "5"))

        restart_policy: str = request.POST.get("restart_policy", "on-failure")
        restart_policy = cast("Literal['always', 'on-failure']", restart_policy)
        restart_policy_dict: _RestartPolicy = {"Name": restart_policy, "MaximumRetryCount": max_retries}

        # Create and start the container with the provided configurations
        container: Container = client.containers.run(
            image=image,
            name=name,
            detach=True,
            ports=ports,
            volumes=binds,
            environment=env_vars,
            restart_policy=restart_policy_dict,
        )

        logger.info("Container %s created successfully with ID %s", name, container.id)
        return HttpResponseRedirect(reverse("container_details", args=[container.id]))


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
def container_details(request: HttpRequest, container_id: str) -> HttpResponse:  # noqa: PLR0914
    """Show details for a specific container.

    Args:
        request (HttpRequest): The request object.
        container_id (str): The ID of the container to show details for.

    Returns:
        HttpResponse: The response object containing container details.
    """
    with DockerClient() as client:
        container = client.containers.get(container_id)

    # Get log parameters from request
    tail_param = request.GET.get("tail", "all")
    tail: int | Literal["all"] = int(tail_param) if tail_param.isdigit() else "all"
    timestamps: bool = request.GET.get("timestamps", "false").lower() == "true"
    since_param = request.GET.get("since")
    since: datetime | float | None = float(since_param) if since_param and since_param.isdigit() else None
    until_param = request.GET.get("until")
    until: datetime | float | None = float(until_param) if until_param and until_param.isdigit() else None
    follow: bool | None = request.GET.get("follow", "false").lower() == "true"

    container_stats = container.stats(stream=False)
    logs: str = container.logs(tail=tail, timestamps=timestamps, since=since, until=until, follow=follow).decode("utf-8")

    # Convert ansi codes to HTML
    logs = remove_ansi(logs)

    # Extract and sort environment variables alphabetically
    env_vars: list[str] = container.attrs.get("Config", {}).get("Env", [])
    sorted_env_vars: list[str] = sorted(env_vars)

    # Format environment variables for display
    # Blur sensitive information and convert URLs to clickable links
    url_pattern: re.Pattern[str] = re.compile(r"(https?://\S+)")
    formatted_env_vars: list[str] = []
    blur_list: list[str] = ["SECRET", "TOKEN", "PASSWORD"]
    for env in sorted_env_vars:
        key, value = env.split("=", 1)
        if any(blur in key for blur in blur_list):
            formatted_env_vars.append(
                format_html(
                    '{}=<span class="blurred" onclick="this.classList.remove(\'blurred\')">{}</span>',
                    key,
                    value,
                )
            )
        else:
            formatted_env_vars.append(format_html(url_pattern.sub(r'<a href="\1">\1</a>', env)))

    context: dict[str, Any] = {
        "container": container,
        "container_stats": container_stats,
        "logs": logs,
        "sorted_env_vars": formatted_env_vars,
        "container_metadata": container.attrs.get("Config", {}).get("Labels", {}),
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
