from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, Literal, cast

from django.conf import settings
from django.contrib.auth.decorators import login_not_required  # pyright: ignore[reportAttributeAccessIssue]
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from docker import errors
from docker.models.networks import Network

from dwui.console import remove_ansi
from dwui.data_importer import add_data_to_model, download_json
from dwui.docker_helper import DockerClient
from dwui.forms import SettingsForm
from dwui.models import AdminSettings, Linuxserver
from dwui.notifications import send_notification

if TYPE_CHECKING:
    from datetime import datetime

    from django.http import HttpRequest
    from docker.models.containers import Container, _RestartPolicy
    from docker.models.images import Image
    from docker.models.networks import Network
    from docker.models.volumes import Volume

logger: logging.Logger = logging.getLogger("dwui.views")


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

        context: dict[str, Any] = {
            "version": current_version_info,
        }

    return render(request, "index.html", context)


def create_container(request: HttpRequest, name: str, image: str) -> HttpResponse:  # noqa: C901, PLR0912, PLR0914
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

        # Process device mappings from form - only include enabled devices
        devices = []
        for key, value in request.POST.items():
            if key.startswith("device_") and key.endswith("_enabled") and value == "on":
                device_id = key.split("_")[1]
                device_path = request.POST.get(f"device_{device_id}_path")
                host_path = request.POST.get(f"device_{device_id}_host_path")
                if device_path and host_path:
                    devices.append(f"{host_path}:{device_path}")

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
            devices=devices,  # Add the devices parameter
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
        HttpResponse: The response for the new container form.
    """
    if request.method == "POST":
        name: str | None = request.POST.get("name")
        image: str | None = request.POST.get("image")

        if name and image:
            return create_container(request, name, image)

    # Fetch Linuxserver data and prepare a flat list of images
    linuxserver_data = Linuxserver.objects.all()

    images: list[dict[str, str]] = [
        {
            "name": str(container_image.name),
            "display_name": str(container_image.name),
            "description": str(container_image.description),
            "project_logo": str(container_image.project_logo),
        }
        for container_image in linuxserver_data
    ]

    context: dict[str, Any] = {
        "images": images,
    }

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
                ),
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
def image_config(request: HttpRequest) -> HttpResponse:  # noqa: C901, PLR0912
    """Handle htmx request for container image configuration.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response containing the configuration form.
    """
    image_name: str = request.GET.get("image", "")
    display_name: str = request.GET.get("display_name", "")

    if not image_name:
        return HttpResponse("Image name is required", status=400)

    # Get default mount paths from admin settings
    try:
        admin_settings = AdminSettings.objects.get(site_id=settings.SITE_ID)
        default_data_path = admin_settings.default_data_path
        default_config_path = admin_settings.default_config_path
    except AdminSettings.DoesNotExist:
        default_data_path = ""
        default_config_path = ""

    # Get container image configuration from the database
    try:
        # Try to fetch configuration from Linuxserver database
        linuxserver_image = Linuxserver.objects.filter(name=image_name).first()

        if linuxserver_image:
            # Convert model instance to a dictionary for the template
            image_config_dict = {
                "name": linuxserver_image.name,
                "display_name": display_name or linuxserver_image.name,  # Use display_name or fallback to name
                "description": linuxserver_image.description,
                "project_logo": linuxserver_image.project_logo,
                "github_url": linuxserver_image.github_url,
                "project_url": linuxserver_image.project_url,
                "ports": [],
                "volumes": [],
                "env_vars": [],
                "devices": [],
            }

            # Add any port mappings from the configuration
            if linuxserver_image.config:
                config = linuxserver_image.config

                # Add ports if defined
                if "ports" not in image_config_dict or not isinstance(image_config_dict["ports"], list):
                    image_config_dict["ports"] = []
                for port in config.ports.all():
                    image_config_dict["ports"].append({
                        "container": port.internal,
                        "host": port.external,
                        "protocol": "tcp",  # Default to TCP
                        "description": port.description,
                    })

                # Add volumes if defined
                for volume in config.volumes.all():
                    if "volumes" not in image_config_dict or not isinstance(image_config_dict["volumes"], list):
                        image_config_dict["volumes"] = []

                    # Determine appropriate default path based on volume purpose
                    default_source = ""
                    if default_data_path and (
                        "/data" in volume.path or "downloads" in volume.path.lower() or "media" in volume.path.lower()
                    ):
                        # Use default data path for data volumes
                        default_source = f"{default_data_path}/{linuxserver_image.name}"
                    elif default_config_path and (
                        "/config" in volume.path or "db" in volume.path.lower() or "database" in volume.path.lower()
                    ):
                        # Use default config path for configuration volumes
                        default_source = f"{default_config_path}/{linuxserver_image.name}"
                    else:
                        # Use the host_path from the configuration or an empty string
                        default_source = volume.host_path

                    image_config_dict["volumes"].append({
                        "target": volume.path,
                        "source": default_source,
                        "description": volume.description,
                        "required": not volume.optional,
                    })

                # Add environment variables if defined
                for env in config.env_vars.all():
                    if "env_vars" not in image_config_dict or not isinstance(image_config_dict["env_vars"], list):
                        image_config_dict["env_vars"] = []
                    image_config_dict["env_vars"].append({
                        "name": env.name,
                        "value": env.value,
                        "description": env.description,
                        "required": not env.optional,
                    })

                # Add devices if defined
                for device in config.devices.all():
                    if "devices" not in image_config_dict or not isinstance(image_config_dict["devices"], list):
                        image_config_dict["devices"] = []
                    image_config_dict["devices"].append({"path": device.path, "host_path": device.host_path, "desc": device.description})
        else:
            # For custom Docker Hub images, create a minimal configuration
            image_config_dict = {
                "name": image_name,
                "display_name": display_name or image_name,
                "description": f"Custom Docker image: {image_name}",
                "ports": [],
                "volumes": [],
                "env_vars": [],
                "devices": [],
            }

        # Create a suggested name based on the image display name
        suggested_name: str = display_name.lower().replace(" ", "-").replace("/", "-")
        suggested_name = "".join(c for c in suggested_name if c.isalnum() or c == "-")

        # Get all available networks
        with DockerClient() as client:
            networks = client.networks.list()
            network_options = [
                {"name": network.name, "id": network.id} for network in networks if network.name not in {"host", "none", "bridge"}
            ]

        context: dict[str, Any] = {
            "image_config": image_config_dict,
            "image_name": image_name,
            "image_display_name": display_name or image_name,
            "suggested_name": suggested_name,
            "networks": network_options,
            "default_data_path": default_data_path,
            "default_config_path": default_config_path,
        }

        return render(request, "partials/container_config_form.html", context)

    except Exception as e:
        logger.exception("Error loading image configuration for %s", image_name)
        return HttpResponse(f"Error loading image configuration: {e!s}", status=500)


@login_not_required
def containers(request: HttpRequest) -> HttpResponse:
    """Render a view with a table of all Docker containers.

    Returns:
        HttpResponse: The response object containing the containers view.
    """
    with DockerClient() as client:
        containers = client.containers.list(all=True)
    context = {"containers": containers}
    return render(request, "containers.html", context)


@login_not_required
def networks(request: HttpRequest) -> HttpResponse:
    """Render a view with a table of all Docker networks.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object containing the networks view.
    """
    with DockerClient() as client:
        networks: list[Network] = client.networks.list()

    # Sort networks by name
    networks.sort(key=lambda net: net.name or "")

    # Move host, none and bridge networks to the end of the list
    networks.sort(key=lambda net: net.name in {"host", "none", "bridge"})

    # Filter networks with search query if provided
    search: str = request.GET.get("search", "").strip().lower()
    if search:
        logger.info("Filtering networks with search term: %s", search)
        networks = [
            net
            for net in networks
            if search in (net.name or "").lower()
            or search in (net.short_id or "").lower()
            or search in (net.attrs.get("Created", "")).lower()
            or search in (net.attrs.get("Driver", "")).lower()
            or search in (net.attrs.get("Labels", {}).get("com.docker.compose.network", "N/A")).lower()
            or search in (net.attrs.get("Labels", {}).get("com.docker.compose.project", "N/A")).lower()
        ]

    context: dict[str, list[Network]] = {"networks": networks}

    if request.headers.get("HX-Request"):
        return render(request, "partials/networks_table.html", context)

    return render(request, "networks.html", context)


@login_not_required
def volumes(request: HttpRequest) -> HttpResponse:
    """Render a view with a table of all Docker volumes.

    Args:
        request: HttpRequest object.

    Returns:
        HttpResponse: The response object containing the volumes view.
    """
    with DockerClient() as client:
        volumes: list[Volume] = client.volumes.list()

    # Sort volumes by name
    volumes.sort(key=lambda vol: vol.name or "")

    # Filter volumes with search query if provided
    search: str = request.GET.get("search", "")
    if search:
        logger.info("Filtering volumes with search term: %s", search)
        low_search = search.lower()
        volumes = [
            vol
            for vol in volumes
            if low_search in (vol.name or "").lower()
            or low_search in (str(vol.attrs.get("CreatedAt", ""))).lower()
            or low_search in (str(vol.attrs.get("Driver", ""))).lower()
            or low_search in (str(vol.attrs.get("Mountpoint", ""))).lower()
        ]

    context: dict[str, list[Volume]] = {"volumes": volumes}

    if request.headers.get("HX-Request"):
        return render(request, "partials/volumes_table.html", context)

    return render(request, "volumes.html", context)


@login_not_required
def images(request: HttpRequest) -> HttpResponse:
    """Render a view with a table of all Docker images.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object containing the images view.
    """
    with DockerClient() as client:
        images: list[Image] = client.images.list()

    total_size: int = sum(image.attrs.get("Size", 0) for image in images)

    context: dict[str, list[Image] | float] = {"images": images, "total_size": total_size}

    if request.headers.get("HX-Request"):
        return render(request, "partials/images_table.html", context)

    return render(request, "images.html", context)


@login_not_required
def settings_page(request: HttpRequest) -> HttpResponse:
    """Render the settings page and handle form submission.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    if request.method == "POST":
        form = SettingsForm(request.POST)
        if form.is_valid():
            # Process the form data
            site_name = form.cleaned_data["site_name"]
            enable_notifications = form.cleaned_data["enable_notifications"]
            apprise_urls = form.cleaned_data["apprise_urls"]
            default_data_path = form.cleaned_data["default_data_path"]
            default_config_path = form.cleaned_data["default_config_path"]

            # Save the settings to the database
            AdminSettings.objects.update_or_create(
                site_id=settings.SITE_ID,
                defaults={
                    "site_name": site_name,
                    "enable_notifications": enable_notifications,
                    "apprise_urls": apprise_urls,
                    "default_data_path": default_data_path,
                    "default_config_path": default_config_path,
                },
            )
            return redirect("admin_settings")
    else:
        form = SettingsForm()

    context: dict[str, SettingsForm | Any] = {"form": form, "site_id": settings.SITE_ID}
    return render(request, "admin.html", context)


@login_not_required
def test_notifications(request: HttpRequest) -> JsonResponse:
    """Handle the test notifications request.

    Returns:
        JsonResponse: A JSON response with a success message.
    """
    # This function returns True if all notifications were successfully
    # sent, False if even just one of them fails, and None if no
    # notifications were sent at all.
    success: bool | None = send_notification(
        title="Test Notification",
        body="This is a test notification from the DWUI application.",
    )
    if success is None:
        return JsonResponse({"message": "No notifications were sent."}, status=400)
    if success is False:
        return JsonResponse({"message": "One or more notifications failed to send."}, status=500)
    return JsonResponse({"message": "Test notification sent successfully."})


@login_not_required
def import_data(request: HttpRequest) -> JsonResponse:
    """Handle the import data request.

    Imports data from the LinuxServer.io API and adds it to the database.

    Args:
        request (HttpRequest): The request object.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    try:
        downloaded_json: dict[str, str] | None = download_json()
        if not downloaded_json:
            logger.error("Failed to download JSON data.")
            return JsonResponse({"message": "Failed to download JSON data."}, status=500)
        try:
            add_data_to_model(downloaded_json)
            logger.info("Data imported successfully.")
            return JsonResponse({"message": "Data imported successfully."}, status=200)
        except Exception as e:
            logger.exception("Error importing data")
            return JsonResponse({"message": f"Error importing data: {e!s}"}, status=500)
    except Exception as e:
        logger.exception("Unexpected error during data import")
        return JsonResponse({"message": f"Unexpected error: {e!s}"}, status=500)
