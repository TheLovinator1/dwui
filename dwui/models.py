from __future__ import annotations

import logging
from datetime import UTC, datetime

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
    """Model representing architecture details, aligned with LinuxServer.io API schema."""

    arch = models.TextField(blank=False, default="")
    tag = models.TextField(blank=False, default="")

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
        self.save()
        return self


class Changelog(models.Model):
    """Model representing changelog details, aligned with LinuxServer.io API schema."""

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

        # In API schema, 'date' is a string and 'desc' is the description field
        date_str = data.get("date")
        if date_str and isinstance(date_str, str):
            try:
                self.date = datetime.fromisoformat(date_str)
            except ValueError:
                logger.warning("Invalid date format: %s", date_str)

        self.description = data.get("desc", self.description)
        self.save()
        return self


class Cap(models.Model):
    """Model representing capabilities, aligned with LinuxServer.io API schema."""

    cap_add = models.TextField(blank=False, default="")
    description = models.TextField(blank=False, default="")
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
        self.save()
        return self


class Custom(models.Model):
    """Model representing custom configurations, aligned with LinuxServer.io API schema."""

    name = models.TextField(blank=False, default="")
    name_compose = models.TextField(blank=False, default="")
    value = models.TextField(blank=False, default="")
    description = models.TextField(blank=False, default="")
    optional = models.BooleanField(default=False)
    # API may contain array values which can't be stored directly in TextField
    is_array_value = models.BooleanField(default=False)

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

        # Handle value which could be a string or an array in the API
        value_data = data.get("value", "")
        if isinstance(value_data, list):
            self.value = ", ".join(value_data)
            self.is_array_value = True
        else:
            self.value = value_data
            self.is_array_value = False

        self.description = data.get("desc", self.description)
        self.optional = data.get("optional", self.optional)
        self.save()
        return self


class Device(models.Model):
    """Model representing device or volume configurations, aligned with LinuxServer.io API schema."""

    path = models.TextField(blank=False, default="")
    host_path = models.TextField(blank=False, default="")
    description = models.TextField(blank=False, default="")
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
        self.save()
        return self


class EnvVar(models.Model):
    """Model representing environment variables, aligned with LinuxServer.io API schema."""

    name = models.TextField(blank=False, default="")
    value = models.TextField(blank=False, default="")
    description = models.TextField(blank=False, default="")
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
        self.save()
        return self


class Hostname(models.Model):
    """Model representing hostname configurations, aligned with LinuxServer.io API schema."""

    hostname = models.TextField(blank=False, default="")
    description = models.TextField(blank=False, default="")
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
        self.save()
        return self


class MACAddress(models.Model):
    """Model representing MAC address configurations, aligned with LinuxServer.io API schema."""

    mac_address = models.TextField(blank=False, default="")
    description = models.TextField(blank=False, default="")
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
        self.save()
        return self


class Port(models.Model):
    """Model representing port configurations, aligned with LinuxServer.io API schema."""

    external = models.TextField(blank=False, default="")
    internal = models.TextField(blank=False, default="")
    description = models.TextField(blank=False, default="")
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
        self.save()
        return self


class SecurityOpt(models.Model):
    """Model representing security options, aligned with LinuxServer.io API schema."""

    run_var = models.TextField(blank=False, default="")
    compose_var = models.TextField(blank=False, default="")
    description = models.TextField(blank=False, default="")
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
        self.save()
        return self


class Config(models.Model):
    """Model representing configuration details, aligned with LinuxServer.io API schema."""

    application_setup = models.TextField(blank=True, default="")
    readonly_supported = models.BooleanField(blank=True, null=True, default=False)
    nonroot_supported = models.BooleanField(blank=True, null=True, default=False)
    networking = models.TextField(blank=True, default="")
    privileged = models.BooleanField(blank=True, null=True, default=False)

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
        return self.application_setup or "Configuration"

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
        self.networking = data.get("networking", self.networking)
        self.privileged = data.get("privileged", self.privileged)

        # Save the instance to get an ID *before* handling many-to-many relationships
        self.save()

        # Handle one-to-one relationships that need to be set before saving again
        self._handle_one_to_one_relationships(data)

        # Handle many-to-many relationships after the instance has an ID
        self._handle_many_to_many_relationships(data)

        return self

    def _handle_many_to_many_relationships(self, data: dict) -> None:
        """Handle many-to-many relationships for the Config model."""
        env_vars_data = data.get("env_vars", []) or []
        for env_var_data in env_vars_data:
            env_var = EnvVar()
            env_var.from_dict(env_var_data)
            self.env_vars.add(env_var)

        ports_data = data.get("ports", []) or []
        for port_data in ports_data:
            port = Port()
            port.from_dict(port_data)
            self.ports.add(port)

        devices_data = data.get("devices", []) or []
        for device_data in devices_data:
            device = Device()
            device.from_dict(device_data)
            self.devices.add(device)

        volumes_data = data.get("volumes", []) or []
        for volume_data in volumes_data:
            volume = Device()
            volume.from_dict(volume_data)
            self.volumes.add(volume)

        custom_data = data.get("custom", []) or []
        for custom_data_item in custom_data:
            custom = Custom()
            custom.from_dict(custom_data_item)
            self.custom.add(custom)

        security_opt_data = data.get("security_opt", []) or []
        for security_opt_data_item in security_opt_data:
            security_opt = SecurityOpt()
            security_opt.from_dict(security_opt_data_item)
            self.security_opt.add(security_opt)

        caps_data = data.get("caps", []) or []
        for cap_data in caps_data:
            cap = Cap()
            cap.from_dict(cap_data)
            self.caps.add(cap)

    def _handle_one_to_one_relationships(self, data: dict) -> None:
        """Handle one-to-one relationships for the Config model."""
        hostname_data = data.get("hostname")
        if hostname_data:
            hostname = Hostname()
            hostname.from_dict(hostname_data)
            self.hostname = hostname

        mac_address_data = data.get("mac_address")
        if mac_address_data:
            mac_address = MACAddress()
            mac_address.from_dict(mac_address_data)
            self.mac_address = mac_address


class Tag(models.Model):
    """Model representing tag elements, aligned with LinuxServer.io API schema."""

    tag = models.TextField(blank=False, default="")
    desc = models.TextField(blank=False, default="")

    def __str__(self) -> str:
        return self.tag

    def from_dict(self, data: dict) -> Tag:
        """Create a Tag instance from a dictionary.

        Args:
            data (dict): A dictionary containing tag details.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            Tag: An instance of the Tag model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.tag = data.get("tag", self.tag)
        self.desc = data.get("desc", self.desc)
        self.save()
        return self


class Linuxserver(models.Model):
    """Model representing Linux server details, aligned with LinuxServer.io API schema."""

    name = models.TextField(primary_key=True)
    initial_date = models.DateTimeField(blank=True, null=True)
    github_url = models.URLField(blank=True, default="")
    project_url = models.URLField(blank=True, default="")
    project_logo = models.URLField(blank=True, default="")
    description = models.TextField(blank=False, default="")
    version = models.TextField(blank=False, default="")
    version_timestamp = models.DateTimeField(blank=False, null=False)
    category = models.TextField(blank=False, default="")
    stable = models.BooleanField(default=False)
    deprecated = models.BooleanField(default=False)
    stars = models.IntegerField(blank=False)
    monthly_pulls = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
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

        # Handle date fields that come as strings
        initial_date_str = data.get("initial_date")
        if initial_date_str and isinstance(initial_date_str, str):
            try:
                self.initial_date = datetime.fromisoformat(initial_date_str)
            except ValueError:
                logger.warning("Invalid initial_date format: %s", initial_date_str)

        version_timestamp_str = data.get("version_timestamp")
        if version_timestamp_str and isinstance(version_timestamp_str, str):
            try:
                self.version_timestamp = datetime.fromisoformat(version_timestamp_str)
            except ValueError:
                logger.warning("Invalid version_timestamp format: %s", version_timestamp_str)
                # Fallback to current time if conversion fails
                self.version_timestamp = datetime.now(tz=UTC)

        # Handle required fields from the API schema
        self.github_url = data.get("github_url", self.github_url)
        self.project_url = data.get("project_url", self.project_url)
        self.project_logo = data.get("project_logo", self.project_logo)
        self.description = data.get("description", self.description)
        self.version = data.get("version", self.version)
        self.category = data.get("category", self.category)
        self.stable = data.get("stable", self.stable)
        self.deprecated = data.get("deprecated", self.deprecated)
        self.stars = data.get("stars", 0)
        self.monthly_pulls = data.get("monthly_pulls", self.monthly_pulls)

        # Save the instance to get an ID (primary key) before handling relationships
        self.save()

        # Handle one-to-one relationships first
        self._handle_one_to_one_relationships(data)

        # Handle many-to-many relationships after the instance has a primary key
        self._handle_many_to_many_relationships(data)

        # Save again after relationships are established
        self.save()
        return self

    def _handle_many_to_many_relationships(self, data: dict) -> None:
        """Handle many-to-many relationships for the Linuxserver model."""
        tags_data = data.get("tags", []) or []
        for tag_data in tags_data:
            tag = Tag()
            tag.from_dict(tag_data)
            self.tags.add(tag)

        architectures_data = data.get("architectures", []) or []
        for architecture_data in architectures_data:
            architecture = Architecture()
            architecture.from_dict(architecture_data)
            self.architectures.add(architecture)

        changelog_data = data.get("changelog", []) or []
        for changelog_item in changelog_data:
            changelog = Changelog()
            changelog.from_dict(changelog_item)
            self.changelog.add(changelog)

    def _handle_one_to_one_relationships(self, data: dict) -> None:
        """Handle one-to-one relationships for the Linuxserver model."""
        config_data = data.get("config")
        if config_data:
            config = Config()
            config.from_dict(config_data)
            self.config = config


class ImagesResponse(models.Model):
    """Model representing the top-level response from the LinuxServer.io API."""

    status = models.TextField(blank=False, default="")
    last_updated = models.DateTimeField()

    def __str__(self) -> str:
        return f"Images Response: {self.status} (Last updated: {self.last_updated})"

    def from_dict(self, data: dict) -> ImagesResponse:
        """Create an ImagesResponse instance from a dictionary.

        Args:
            data (dict): A dictionary containing the API response.

        Raises:
            TypeError: If the input data is not a dictionary.

        Returns:
            ImagesResponse: An instance of the ImagesResponse model populated with data from the dictionary.
        """
        if not isinstance(data, dict):
            msg = f"Expected a dictionary but got {type(data).__name__}."
            raise TypeError(msg)

        self.status = data.get("status", self.status)

        last_updated_str = data.get("last_updated")
        if last_updated_str and isinstance(last_updated_str, str):
            try:
                self.last_updated = datetime.fromisoformat(last_updated_str)
            except ValueError:
                logger.warning("Invalid last_updated format: %s", last_updated_str)
                self.last_updated = datetime.now(tz=UTC)

        self.save()
        return self
