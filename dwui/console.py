from __future__ import annotations

import logging
import re

logger: logging.Logger = logging.getLogger("dwui")

# ANSI escape code regex pattern
ansi_escape: re.Pattern[str] = re.compile(r"\x1b\[(?P<code>[0-9;]+)m")


def remove_ansi(text: str) -> str:
    """Remove ANSI escape codes from a string.

    Args:
        text (str): The input string containing ANSI escape codes.

    Returns:
        str: The input string with ANSI escape codes removed.
    """
    # Use regex to remove ANSI escape sequences
    cleaned_text = ansi_escape.sub("", text)

    logger.debug("Removed ANSI codes from text: %s", cleaned_text)

    return cleaned_text
