from __future__ import annotations

from django import forms


class SettingsForm(forms.Form):
    """Form to handle application settings."""

    site_name = forms.CharField(label="Site Name", max_length=100)
    admin_email = forms.EmailField(label="Admin Email")
    enable_notifications = forms.BooleanField(label="Enable Notifications", required=False)
