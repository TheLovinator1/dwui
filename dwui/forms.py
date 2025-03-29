from __future__ import annotations

from typing import Any

from django import forms
from django.conf import settings

from dwui.models import AdminSettings


class SettingsForm(forms.Form):
    """Form to handle application settings."""

    site_name = forms.CharField(label="Site Name", max_length=100, initial="dwui")
    site_name.help_text = "Site Name. Used in notifications and the title of the site."
    site_name.widget.attrs.update({"placeholder": "Site Name"})

    apprise_urls = forms.CharField(
        label="Apprise URLs",
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": "Newline separated list of apprise URLs"}),
        required=False,
        help_text="A newline-separated list of URLs for notifications. # or // to disable URLs.",
    )
    enable_notifications = forms.BooleanField(
        label="Enable Notifications",
        required=False,
        initial=False,
        help_text="Flag to enable or disable notifications",
    )

    default_data_path = forms.CharField(
        label="Default Data Path",
        max_length=500,
        required=False,
        initial="",
        help_text="Default path for container data storage (e.g., HDD path like /mnt/storage/data)",
        widget=forms.TextInput(attrs={"placeholder": "/mnt/storage/data"}),
    )

    default_config_path = forms.CharField(
        label="Default Config Path",
        max_length=500,
        required=False,
        initial="",
        help_text="Default path for container configuration storage (e.g., NVMe path like /mnt/nvme/configs)",
        widget=forms.TextInput(attrs={"placeholder": "/mnt/nvme/configs"}),
    )

    def __init__(self, *args: Any, **kwargs: dict[str, Any]) -> None:  # noqa: ANN401
        """Initialize the form with existing settings."""
        super().__init__(*args, **kwargs)
        try:
            settings_instance: AdminSettings = AdminSettings.objects.get(site_id=settings.SITE_ID)
            self.fields["site_name"].initial = settings_instance.site_name
            self.fields["apprise_urls"].initial = settings_instance.apprise_urls
            self.fields["enable_notifications"].initial = settings_instance.enable_notifications
            self.fields["default_data_path"].initial = settings_instance.default_data_path
            self.fields["default_config_path"].initial = settings_instance.default_config_path
        except AdminSettings.DoesNotExist:
            self.fields["site_name"].initial = ""
            self.fields["apprise_urls"].initial = ""
            self.fields["enable_notifications"].initial = False
            self.fields["default_data_path"].initial = ""
            self.fields["default_config_path"].initial = ""
