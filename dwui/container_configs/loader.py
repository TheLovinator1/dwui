"""Helper module for loading container configurations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dwui.container_configs.adguard_home import ADGUARD_HOME_SYNC

if TYPE_CHECKING:
    from dwui.container_config import ContainerImageConfig

# List of all container configurations
# Add new configurations here as they are created
ALL_CONTAINER_CONFIGS: list[ContainerImageConfig] = [
    ADGUARD_HOME_SYNC,
]


def get_all_container_configs() -> list[ContainerImageConfig]:
    """Get all available container configurations.

    Returns:
        List[ContainerImageConfig]: List of all container configurations.
    """
    return ALL_CONTAINER_CONFIGS
