from __future__ import annotations

import logging

from django.contrib.auth.models import AbstractUser
from django.db import models

logger: logging.Logger = logging.getLogger("dwui")


class CustomUser(AbstractUser):
    """CustomUser model that extends the default Django AbstractUser.

    This model can be used to add additional fields or methods to the default user model provided by Django.

    Attributes:
        Inherits all attributes from AbstractUser.
    """


class AdminSettings(models.Model):
    """A Django model representing the administrative settings for a web application.

    Attributes:
        site_name (str): The name of the site.
        enable_notifications (bool): Flag to enable or disable notifications.
        apprise_urls (str): A newline-separated list of URLs for notifications.

    Methods:
        __str__(): Returns the site name as the string representation of the model.
    """

    site_id = models.AutoField(primary_key=True, help_text="Site ID")
    site_name = models.TextField(blank=True, max_length=100, default="dwui", help_text="Site Name")
    enable_notifications = models.BooleanField(default=False, help_text="Send notifications to apprise URLs")
    apprise_urls = models.TextField(blank=True, help_text="Newline separated list of apprise URLs")

    def __str__(self) -> str:
        """Return the site name."""
        return self.site_name


class Architecture(models.Model):
    """Model representing architecture details."""

    arch = models.TextField(blank=True, default="")
    tag = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return f"{self.arch} - {self.tag}"

    def from_dict(self, data: dict) -> Architecture:
        """Create an Architecture instance from a dictionary.

        Args:
            data (dict): A dictionary containing architecture details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            Architecture: An instance of the Architecture model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.arch = data.get("arch", self.arch)
        self.tag = data.get("tag", self.tag)
        return self


class Changelog(models.Model):
    """Model representing changelog details."""

    date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return f"{self.date}: {self.description}"

    def from_dict(self, data: dict) -> Changelog:
        """Create a Changelog instance from a dictionary.

        Args:
            data (dict): A dictionary containing changelog details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            Changelog: An instance of the Changelog model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.date = data.get("date", self.date)
        self.description = data.get("desc", self.description)
        return self


class Cap(models.Model):
    """Model representing capabilities."""

    cap_add = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    optional = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.cap_add

    def from_dict(self, data: dict) -> Cap:
        """Create a Cap instance from a dictionary.

        Args:
            data (dict): A dictionary containing capability details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            Cap: An instance of the Cap model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.cap_add = data.get("cap_add", self.cap_add)
        self.description = data.get("desc", self.description)
        self.optional = data.get("optional", self.optional)
        return self


class Custom(models.Model):
    """Model representing custom configurations."""

    name = models.TextField(blank=True, default="")
    name_compose = models.TextField(blank=True, default="")
    value = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    optional = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    def from_dict(self, data: dict) -> Custom:
        """Create a Custom instance from a dictionary.

        Args:
            data (dict): A dictionary containing custom configuration details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            Custom: An instance of the Custom model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.name = data.get("name", self.name)
        self.name_compose = data.get("name_compose", self.name_compose)
        self.value = data.get("value", self.value)
        self.description = data.get("desc", self.description)
        return self


class Device(models.Model):
    """Model representing device configurations."""

    path = models.TextField(blank=True, default="")
    host_path = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    optional = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.path

    def from_dict(self, data: dict) -> Device:
        """Create a Device instance from a dictionary.

        Args:
            data (dict): A dictionary containing device configuration details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            Device: An instance of the Device model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.path = data.get("path", self.path)
        self.host_path = data.get("host_path", self.host_path)
        self.description = data.get("desc", self.description)
        self.optional = data.get("optional", self.optional)

        return self


class EnvVar(models.Model):
    """Model representing environment variables."""

    name = models.TextField(blank=True, default="")
    value = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    optional = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    def from_dict(self, data: dict) -> EnvVar:
        """Create an EnvVar instance from a dictionary.

        Args:
            data (dict): A dictionary containing environment variable details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            EnvVar: An instance of the EnvVar model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.name = data.get("name", self.name)
        self.value = data.get("value", self.value)
        self.description = data.get("desc", self.description)
        self.optional = data.get("optional", self.optional)

        return self


class Hostname(models.Model):
    """Model representing hostname configurations."""

    hostname = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    optional = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.hostname

    def from_dict(self, data: dict) -> Hostname:
        """Create a Hostname instance from a dictionary.

        Args:
            data (dict): A dictionary containing hostname details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            Hostname: An instance of the Hostname model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.hostname = data.get("hostname", self.hostname)
        self.description = data.get("desc", self.description)
        self.optional = data.get("optional", self.optional)

        return self


class MACAddress(models.Model):
    """Model representing MAC address configurations."""

    mac_address = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    optional = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.mac_address

    def from_dict(self, data: dict) -> MACAddress:
        """Create a MACAddress instance from a dictionary.

        Args:
            data (dict): A dictionary containing MAC address details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            MACAddress: An instance of the MACAddress model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.mac_address = data.get("mac_address", self.mac_address)
        self.description = data.get("desc", self.description)
        self.optional = data.get("optional", self.optional)

        return self


class Port(models.Model):
    """Model representing port configurations."""

    external = models.TextField(blank=True, default="")
    internal = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    optional = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.external}:{self.internal}"

    def from_dict(self, data: dict) -> Port:
        """Create a Port instance from a dictionary.

        Args:
            data (dict): A dictionary containing port details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            Port: An instance of the Port model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.external = data.get("external", self.external)
        self.internal = data.get("internal", self.internal)
        self.description = data.get("desc", self.description)
        self.optional = data.get("optional", self.optional)

        return self


class SecurityOpt(models.Model):
    """Model representing security options."""

    run_var = models.TextField(blank=True, default="")
    compose_var = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    optional = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.run_var

    def from_dict(self, data: dict) -> SecurityOpt:
        """Create a SecurityOpt instance from a dictionary.

        Args:
            data (dict): A dictionary containing security option details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            SecurityOpt: An instance of the SecurityOpt model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.run_var = data.get("run_var", self.run_var)
        self.compose_var = data.get("compose_var", self.compose_var)
        self.description = data.get("desc", self.description)
        self.optional = data.get("optional", self.optional)

        return self


class Config(models.Model):
    """Model representing configuration details."""

    application_setup = models.TextField(blank=True, default="")
    readonly_supported = models.BooleanField(default=False)
    nonroot_supported = models.BooleanField(default=False)
    networking = models.TextField(blank=True, default="")
    privileged = models.BooleanField(default=False)

    # The following fields are one-to-one relationships
    hostname = models.OneToOneField(Hostname, on_delete=models.CASCADE, blank=True, null=True)
    mac_address = models.OneToOneField(MACAddress, on_delete=models.CASCADE, blank=True, null=True)

    # The following fields are many-to-many relationships
    env_vars = models.ManyToManyField(EnvVar, blank=True)
    volumes = models.ManyToManyField(Device, related_name="config_volumes", blank=True)
    ports = models.ManyToManyField(Port, blank=True)
    devices = models.ManyToManyField(Device, related_name="config_devices", blank=True)
    custom = models.ManyToManyField(Custom, blank=True)
    security_opt = models.ManyToManyField(SecurityOpt, blank=True)
    caps = models.ManyToManyField(Cap, blank=True)

    def __str__(self) -> str:
        return self.application_setup

    def from_dict(self, data: dict) -> Config:
        """Create a Config instance from a dictionary.

        Args:
            data (dict): A dictionary containing configuration details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            Config: An instance of the Config model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.application_setup = data.get("application_setup", self.application_setup)
        self.readonly_supported = data.get("readonly_supported", self.readonly_supported)
        self.nonroot_supported = data.get("nonroot_supported", self.nonroot_supported)

        self._handle_many_to_many_relationships(data)
        self._handle_one_to_one_relationships(data)

        self.save()

        return self

    def _handle_many_to_many_relationships(self, data: dict) -> None:  # noqa: C901
        """Handle many-to-many relationships for the Config model."""
        env_vars_data = data.get("env_vars", [])
        for env_var_data in env_vars_data:
            env_var, created = EnvVar.objects.get_or_create(
                name=env_var_data.get("name", ""),
                value=env_var_data.get("value", ""),
                description=env_var_data.get("desc", ""),
                optional=env_var_data.get("optional", False),
            )
            if created:
                logger.info("Created new environment variable: %s", env_var)
            self.env_vars.add(env_var)

        ports_data = data.get("ports", [])
        for port_data in ports_data:
            port, created = Port.objects.get_or_create(
                external=port_data.get("external", ""),
                internal=port_data.get("internal", ""),
                description=port_data.get("desc", ""),
                optional=port_data.get("optional", False),
            )
            if created:
                logger.info("Created new port configuration: %s", port)
            self.ports.add(port)

        devices_data = data.get("devices", [])
        for device_data in devices_data:
            device, created = Device.objects.get_or_create(
                path=device_data.get("path", ""),
                host_path=device_data.get("host_path", ""),
                description=device_data.get("desc", ""),
                optional=device_data.get("optional", False),
            )
            if created:
                logger.info("Created new device configuration: %s", device)
            self.devices.add(device)

        custom_data = data.get("custom", [])
        for custom_data_item in custom_data:
            custom, created = Custom.objects.get_or_create(
                name=custom_data_item.get("name", ""),
                name_compose=custom_data_item.get("name_compose", ""),
                value=custom_data_item.get("value", ""),
                description=custom_data_item.get("desc", ""),
                optional=custom_data_item.get("optional", False),
            )
            if created:
                logger.info("Created new custom configuration: %s", custom)
            self.custom.add(custom)

        security_opt_data = data.get("security_opt", [])
        for security_opt_data_item in security_opt_data:
            security_opt, created = SecurityOpt.objects.get_or_create(
                run_var=security_opt_data_item.get("run_var", ""),
                compose_var=security_opt_data_item.get("compose_var", ""),
                description=security_opt_data_item.get("desc", ""),
                optional=security_opt_data_item.get("optional", False),
            )
            if created:
                logger.info("Created new security option: %s", security_opt)
            self.security_opt.add(security_opt)

        caps_data = data.get("caps", [])
        for cap_data in caps_data:
            cap, created = Cap.objects.get_or_create(
                cap_add=cap_data.get("cap_add", ""),
                description=cap_data.get("desc", ""),
                optional=cap_data.get("optional", False),
            )
            if created:
                logger.info("Created new capability: %s", cap)

            self.caps.add(cap)

    def _handle_one_to_one_relationships(self, data: dict) -> None:
        """Handle one-to-one relationships for the Config model."""
        hostname_data = data.get("hostname", {})
        self.hostname, created = Hostname.objects.get_or_create(
            hostname=hostname_data.get("hostname", ""),
            description=hostname_data.get("desc", ""),
            optional=hostname_data.get("optional", False),
        )
        if created:
            logger.info("Created new hostname: %s", self.hostname)

        mac_address_data = data.get("mac_address", {})
        self.mac_address, created = MACAddress.objects.get_or_create(
            mac_address=mac_address_data.get("mac_address", ""),
            description=mac_address_data.get("desc", ""),
            optional=mac_address_data.get("optional", False),
        )
        if created:
            logger.info("Created new MAC address: %s", self.mac_address)


class TagElement(models.Model):
    """Model representing tag elements."""

    tag = models.TextField(blank=True, default="")
    desc = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.tag


class Linuxserver(models.Model):
    """Model representing Linux server details."""

    name = models.TextField(primary_key=True)
    initial_date = models.DateTimeField(blank=True, null=True)
    github_url = models.URLField(blank=True, default="")
    project_url = models.URLField(blank=True, default="")
    project_logo = models.URLField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    version = models.TextField(blank=True, default="")
    version_timestamp = models.DateTimeField(blank=True, null=True)
    category = models.TextField(blank=True, default="")
    stable = models.BooleanField(default=False)
    deprecated = models.BooleanField(default=False)
    stars = models.IntegerField(blank=True, null=True)
    monthly_pulls = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField(TagElement, blank=True)
    architectures = models.ManyToManyField(Architecture, blank=True)
    changelog = models.ManyToManyField(Changelog, blank=True)
    config = models.OneToOneField(Config, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def from_dict(self, data: dict) -> Linuxserver:
        """Create a Linuxserver instance from a dictionary.

        Args:
            data (dict): A dictionary containing Linux server details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            Linuxserver: An instance of the Linuxserver model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.initial_date = data.get("initial_date", self.initial_date)
        self.github_url = data.get("github_url", self.github_url)
        self.project_url = data.get("project_url", self.project_url)
        self.project_logo = data.get("project_logo", self.project_logo)
        self.description = data.get("description", self.description)
        self.version = data.get("version", self.version)
        self.version_timestamp = data.get("version_timestamp", self.version_timestamp)
        self.category = data.get("category", self.category)
        self.stable = data.get("stable", self.stable)
        self.deprecated = data.get("deprecated", self.deprecated)
        self.stars = data.get("stars", self.stars)
        self.monthly_pulls = data.get("monthly_pulls", self.monthly_pulls)

        self._handle_many_to_many_relationships(data)
        self._handle_one_to_one_relationships(data)

        self.save()
        return self

    def _handle_many_to_many_relationships(self, data: dict) -> None:
        """Handle many-to-many relationships for the Linuxserver model."""
        tags_data = data.get("tags", [])
        for tag_data in tags_data:
            tag, created = TagElement.objects.get_or_create(
                tag=tag_data.get("tag", ""),
                desc=tag_data.get("desc", ""),
            )
            if created:
                logger.info("Created new tag: %s", tag)

            self.tags.add(tag)

        architectures_data = data.get("architectures", [])
        for architecture_data in architectures_data:
            architecture, created = Architecture.objects.get_or_create(
                arch=architecture_data.get("arch", ""),
                tag=architecture_data.get("tag", ""),
            )
            if created:
                logger.info("Created new architecture: %s", architecture)
            self.architectures.add(architecture)

        changelog_data = data.get("changelog", [])
        for changelog_item in changelog_data:
            changelog, created = Changelog.objects.get_or_create(
                date=changelog_item.get("date", None),
                description=changelog_item.get("desc", ""),
            )
            if created:
                logger.info("Created new changelog: %s", changelog)
            self.changelog.add(changelog)

    def _handle_one_to_one_relationships(self, data: dict) -> None:
        """Handle one-to-one relationships for the Linuxserver model."""
        config_data = data.get("config", {})
        self.config, created = Config.objects.get_or_create(
            application_setup=config_data.get("application_setup", ""),
            readonly_supported=config_data.get("readonly_supported", False),
            nonroot_supported=config_data.get("nonroot_supported", False),
            networking=config_data.get("networking", ""),
            privileged=config_data.get("privileged", False),
        )
        if created:
            logger.info("Created new config: %s", self.config)
        self.config.save()
