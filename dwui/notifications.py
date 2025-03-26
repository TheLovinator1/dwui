from __future__ import annotations

import logging

import apprise

from dwui.models import AdminSettings

logger: logging.Logger = logging.getLogger("dwui")


def send_notification(title: str, body: str) -> bool | None:
    """Send a notification using Apprise.

    Args:
        title (str): The title of the notification.
        body (str): The body of the notification. This can be formatted using Markdown.

    Returns:
        (bool | None): This function returns True if all notifications were successfully
          sent, False if even just one of them fails, and None if no
          notifications were sent at all.
    """
    if not title:
        title = "dwui Notification"

    if not body:
        body = "No message provided."

    try:
        settings: AdminSettings | None = AdminSettings.objects.first()
        if settings and settings.enable_notifications:
            apprise_obj = apprise.Apprise()

            apprise_urls: list[str] = settings.apprise_urls.splitlines()

            # Remove any URLs that start with # or //
            apprise_urls = [url for url in apprise_urls if not url.startswith(("#", "//"))]

            if apprise_urls:
                for url in apprise_urls:
                    apprise_obj.add(url)

            success: bool | None = apprise_obj.notify(
                body=body,
                title=title,
                body_format=apprise.NotifyFormat.MARKDOWN,
            )

            msg: str = "Notifications sent successfully." if success else "One or more notifications failed to send."
            logger.info(msg)

            return success

        logger.info("Notifications are disabled or no settings found.")

    except TypeError:
        logger.exception("Error sending notifications:\nTitle: %s\nBody: %s\n", title, body)

    return None
