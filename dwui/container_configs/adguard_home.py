from __future__ import annotations

from dwui.container_config import ContainerImageConfig, EnvVarConfig, PortConfig, VolumeConfig

ADGUARD_HOME_SYNC: ContainerImageConfig = ContainerImageConfig.create_complete(
    name="AdGuard Home Sync",
    image="lscr.io/linuxserver/adguardhome-sync:latest",
    description="adguardhome-sync is a tool to synchronize AdGuardHome config to replica instances.",
    category="Network,DNS",
    initial_date="2021-04-08",
    github_url="https://github.com/linuxserver/docker-adguardhome-sync",
    project_url="https://github.com/bakito/adguardhome-sync/",
    project_logo="https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/adguardhomesync-icon.png",
    application_setup="https://github.com/linuxserver/docker-airsonic-advanced?tab=readme-ov-file#application-setup",
    nonroot_supported=True,
    readonly_supported=True,
    stable=True,
    deprecated=False,
    tags=[{"tag": "latest", "desc": "Stable releases"}],
    architectures=[{"arch": "x86_64", "tag": "amd64-latest"}, {"arch": "arm64", "tag": "arm64v8-latest"}],
    volumes=[
        VolumeConfig(source="/path/to/adguardhome-sync/config", target="/config", description="Contains all relevant configuration files."),
    ],
    ports=[
        PortConfig(external="8080", internal="8080", protocol="tcp", desc="Port for AdGuardHome Sync's web API."),
    ],
    env_vars=[
        EnvVarConfig(
            name="CONFIGFILE",
            value="/config/adguardhome-sync.yaml",
            description="Set a custom config file.",
            optional=True,
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
