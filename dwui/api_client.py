"""API client for communicating with the Docker agent.

This module provides a client for making API requests to the Docker agent,
which handles the actual Docker operations. It abstracts away the HTTP
communication details and provides a clean interface for the DWUI application.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import requests
from django.conf import settings
from requests.exceptions import RequestException

logger: logging.Logger = logging.getLogger("dwui.api_client")


class APIClient:
    """Client for making API requests to the Docker agent."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize the API client.

        Args:
            base_url: The base URL of the Docker agent API. If not provided,
                it will be read from Django settings.
        """
        self.base_url: str = base_url or settings.DWUI_AGENT_API_URL
        logger.debug("Initialized API client with base URL: %s", self.base_url)

    def _handle_request_error(self, method: str, url: str, error: Exception) -> dict[str, Any]:  # noqa: PLR6301
        """Handle request errors.

        Args:
            method: The HTTP method that was used.
            url: The URL that was requested.
            error: The exception that was raised.

        Returns:
            A dictionary with error information.
        """
        logger.error("API request failed: %s %s", method, url)
        return {
            "error": True,
            "message": f"API request failed: {error!s}",
            "status_code": getattr(error, "status_code", 500) if hasattr(error, "status_code") else 500,
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the API.

        Args:
            method: The HTTP method to use.
            endpoint: The API endpoint to request.
            data: The data to send in the request body.
            params: The query parameters to include in the request.

        Raises:
            ValueError: If an unsupported HTTP method is used.

        Returns:
            The API response data as a dictionary.
        """
        url: str = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        logger.debug("Making %s request to %s", method, url)

        try:
            if method.upper() == "GET":
                response: requests.Response = requests.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response: requests.Response = requests.post(url, json=data, timeout=30)
            elif method.upper() == "PUT":
                response: requests.Response = requests.put(url, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response: requests.Response = requests.delete(url, json=data, timeout=30)
            else:
                msg: str = f"Unsupported HTTP method: {method}"
                raise ValueError(msg)

            response.raise_for_status()

            if response.content:
                return response.json()

        except (RequestException, json.JSONDecodeError) as e:
            return self._handle_request_error(method, url, e)
        else:
            return {"success": True, "status_code": response.status_code}

    def get_all_containers(self) -> dict[str, Any]:
        """Get a list of all containers.

        Returns:
            A list of dictionaries with container details.
        """
        return self._make_request("GET", "/api/v1/containers/")

    def get_container_details(self, container_id: str) -> dict[str, Any]:
        """Get details for a specific container.

        Args:
            container_id: The ID of the container.

        Returns:
            A dictionary with container details.
        """
        return self._make_request("GET", f"/api/v1/containers/{container_id}/")

    def create_container(
        self,
        image: str,
        name: str,
        ports: str = "",
        binds: str = "",
        env_vars: str = "",
        restart_policy: str = "always",
    ) -> dict[str, Any]:
        """Create a new container.

        Args:
            image: The Docker image to use.
            name: The name for the container.
            ports: The ports to expose in format "host_port:container_port/protocol".
            binds: The volumes to bind in format "host_path:container_path[:mode]".
            env_vars: The environment variables in format "KEY=VALUE".
            restart_policy: The restart policy, default is "always".

        Returns:
            A dictionary with the created container details.
        """
        data: dict[str, str] = {
            "image": image,
            "name": name,
            "ports": ports,
            "binds": binds,
            "env_vars": env_vars,
            "restart_policy": restart_policy,
        }
        return self._make_request("POST", "/api/v1/containers/create/", data=data)

    def get_docker_version(self) -> dict[str, Any]:
        """Get the Docker version.

        Returns:
            A dictionary with the Docker version information.
        """
        return self._make_request("GET", "api/v1/docker/version/")
