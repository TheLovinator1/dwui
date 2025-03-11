from __future__ import annotations

from dwui.container_config import ContainerImageConfig, DeviceConfig, EnvVarConfig, PortConfig, VolumeConfig
from dwui.container_configs.host_timezone import get_host_timezone

AIRSONIC: ContainerImageConfig = ContainerImageConfig.create_complete(
    name="Airsonic-Advanced",
    image="airsonic-advanced",
    description="airsonic-advanced is a free, web-based media streamer, providing ubiquitous access to your music. Use it to share your music with friends, or to listen to your own music while at work. You can stream to multiple players simultaneously, for instance to one player in your kitchen and another in your living room.",  # noqa: E501
    category="Media Servers,Music",
    initial_date="2022-01-02",
    github_url="https://github.com/linuxserver/docker-airsonic-advanced",
    project_url="https://github.com/kagemomiji/airsonic-advanced",
    project_logo="https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/airsonic-banner.png",
    stable=True,
    deprecated=False,
    tags=[{"tag": "latest", "desc": "Stable releases"}],
    architectures=[{"arch": "x86_64", "tag": "amd64-latest"}, {"arch": "arm64", "tag": "arm64v8-latest"}],
    volumes=[
        VolumeConfig(source="/path/to/airsonic/config", target="/config", description="Contains all relevant configuration files."),
        VolumeConfig(source="/path/to/airsonic/music", target="/music", description="Music library."),
        VolumeConfig(source="/path/to/airsonic/podcasts", target="/podcasts", description="Podcasts library."),
        VolumeConfig(source="/path/to/airsonic/playlists", target="/playlists", description="Location for playlists to be saved to."),
        VolumeConfig(source="/path/to/airsonic/media", target="/media", description="Location of other media."),
    ],
    ports=[
        PortConfig(external="4040", internal="4040", protocol="tcp", desc="Airsonic web interface."),
    ],
    env_vars=[
        EnvVarConfig(name="TZ", value=get_host_timezone(), description="Timezone", optional=True),
        EnvVarConfig(name="JAVA_OPTS", value="-Xms256m -Xmx512m", description="Java runtime options.", optional=False),
        EnvVarConfig(name="CONTEXT_PATH", value="", description="For setting url-base in reverse proxy setups.", optional=False),
    ],
    devices=[
        DeviceConfig(
            path="/dev/snd",
            host_path="/dev/snd",
            desc="Only needed to pass your host sound device to Airsonic's Java jukebox player.",
            optional=True,
        ),
    ],
    use_common_env_vars=True,
)


def get_airsonic_config() -> dict:
    """Return the Airsonic configuration as a dictionary.

    Returns:
        dict: Airsonic configuration as a dictionary.
    """
    return AIRSONIC.to_dict()
