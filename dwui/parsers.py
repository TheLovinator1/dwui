from __future__ import annotations

import logging
from typing import Any, Literal

from docker.models.containers import _RestartPolicy  # noqa: PLC2701

logger: logging.Logger = logging.getLogger("dwui.agent")


def get_ports(ports: str) -> dict[str, int | list[int] | tuple[str, int] | None] | None:
    """Convert ports to a dictionary format for Docker containers.create().

    Args:
        ports (str): The ports string in 'host_port:container_port/protocol' format.
                     E.g. "8080:80/tcp,9000:9000/udp"

    Returns:
        dict: A dictionary with container ports as keys and host port bindings as values.
             Format: {'container_port/protocol': [{'HostIp': '', 'HostPort': 'host_port'}]}
    """
    if not ports.strip():
        return {}

    port_dict: dict[str, Any] = {}
    for port_mapping in ports.split(","):
        if ":" in port_mapping:
            logger.debug("Parsing port mapping: %s", port_mapping)
            host_port, container_port_with_protocol = port_mapping.split(":")

            # Handle protocol if specified
            if "/" in container_port_with_protocol:
                container_port, protocol = container_port_with_protocol.split("/")
            else:
                container_port, protocol = container_port_with_protocol, "tcp"

            port_key: str = f"{container_port}/{protocol}"
            port_dict[port_key] = [{"HostIp": "", "HostPort": host_port}]

            logger.debug("Parsed port mapping: %s -> %s", host_port, port_key)
        else:
            logger.warning("Invalid port mapping format: %s, skipping", port_mapping)
            continue

    return port_dict


def get_binds(binds: str) -> dict[str, dict[str, str]]:
    """Convert binds to a dictionary format for Docker volumes.

    Args:
        binds (str): The binds string in 'host_path:container_path[:mode]' format,
                    where mode is 'ro' (read-only) or 'rw' (read-write, default).
                    Multiple binds can be separated by commas.
                    For example: "/host/path:/container/path:ro,/data:/data:rw"

    Returns:
        dict[str, dict[str, str]]: A dictionary with host paths as keys and
                                    dictionaries with 'bind' and 'mode' as values.
                                    Example: {'/host/path': {'bind': '/container/path', 'mode': 'ro'}}
    """
    if not binds or not binds.strip():
        return {}

    volumes_dict: dict[str, dict[str, str]] = {}
    for bind in binds.split(","):
        if not bind.strip():
            continue

        parts: list[str] = bind.split(":")

        # Example: "/host/path:/container/path"
        if len(parts) == 2:
            host_path, container_path = parts
            volumes_dict[host_path] = {"bind": container_path, "mode": "rw"}

        # Example: "/host/path:/container/path:ro" or "/host/path:/container/path:rw"
        elif len(parts) == 3:
            host_path, container_path, mode = parts
            if mode not in {"ro", "rw"}:
                logger.warning("Invalid bind mode '%s', defaulting to 'rw'", mode)
                mode = "rw"
            volumes_dict[host_path] = {"bind": container_path, "mode": mode}

        # Example: "/host/path:/container/path:ro:extra"
        else:
            logger.warning("Invalid bind format: %s, skipping", bind)

    logger.debug("Parsed binds: %s", volumes_dict)
    return volumes_dict


def get_env_vars(env_vars: str) -> dict[str, str]:
    """Convert environment variables to a dictionary format.

    Args:
        env_vars (str): The environment variables string in 'key=value' format.

    Returns:
        dict[str, str]: A dictionary with keys and values as strings.
    """
    return dict(env_var.split("=") for env_var in env_vars.split(","))


def get_restart_policy(restart_policy: str | None) -> _RestartPolicy:
    """Convert restart policy to a dictionary format.

    Args:
        restart_policy (str): The restart policy string.

    Returns:
        _RestartPolicy: A dictionary with the restart policy and maximum retry count.
    """
    allowed_policies: set[Literal["always", "on-failure"]] = {"always", "on-failure"}
    if restart_policy not in allowed_policies:
        logger.warning("Invalid restart policy '%s', defaulting to 'on-failure'", restart_policy)
        restart_policy = "on-failure"

    return _RestartPolicy(Name=restart_policy, MaximumRetryCount=3)
