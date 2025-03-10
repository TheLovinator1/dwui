"""AdGuard Home Sync configuration for Docker Web UI."""

from __future__ import annotations

from dwui.container_config import ContainerImageConfig, EnvVarConfig, PortConfig, VolumeConfig

# Create the AdGuard Home Sync configuration
ADGUARD_HOME_SYNC = ContainerImageConfig.create_complete(
    name="AdGuard Home Sync",
    image="linuxserver/adguardhome-sync",
    description="adguardhome-sync is a tool to synchronize AdGuardHome config to replica instances.",
    category="Network,DNS",
    initial_date="2021-04-08",
    github_url="https://github.com/linuxserver/docker-adguardhome-sync",
    project_url="https://github.com/bakito/adguardhome-sync/",
    project_logo="https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/adguardhomesync-icon.png",
    version="v0.7.1-ls131",
    version_timestamp="2025-02-25 20:39:46+00:00",
    stable=True,
    deprecated=False,
    stars=45,
    monthly_pulls=14063,
    tags=[{"tag": "latest", "desc": "Stable releases"}],
    architectures=[{"arch": "x86_64", "tag": "amd64-latest"}, {"arch": "arm64", "tag": "arm64v8-latest"}],
    changelog=[
        {"date": "2024-12-17", "desc": "Rebase to Alpine 3.21."},
        {"date": "2024-05-24", "desc": "Rebase to Alpine 3.20."},
        {"date": "2024-01-31", "desc": "Rebase to Alpine 3.19."},
    ],
    volumes=[
        VolumeConfig(source="/path/to/adguardhome-sync/config", target="/config", description="Contains all relevant configuration files."),
    ],
    ports=[PortConfig(host="8080", container="8080", protocol="tcp", description="Port for AdGuardHome Sync's web API.")],
    env_vars=[
        EnvVarConfig(name="TZ", default="Etc/UTC", description="Timezone", required=True),
        EnvVarConfig(
            name="CONFIGFILE",
            default="/config/adguardhome-sync.yaml",
            description="Set a custom config file.",
            required=False,
        ),
    ],
    use_common_env_vars=True,
)


def get_adguard_home_sync_config() -> dict:
    """Return the AdGuard Home Sync configuration as a dictionary.

    Returns:
        dict: AdGuard Home Sync configuration as a dictionary.
    """
    return ADGUARD_HOME_SYNC.to_dict()
