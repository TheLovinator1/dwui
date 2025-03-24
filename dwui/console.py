from __future__ import annotations

import logging
import re

logger: logging.Logger = logging.getLogger("dwui")

ansi_escape: re.Pattern[str] = re.compile(r"\x1b\[(?P<code>[0-9;]+)m")


def remove_ansi(text: str) -> str:
    """Remove ANSI escape codes from a string.

    Args:
        text (str): The input string containing ANSI escape codes.

    Returns:
        str: The input string with ANSI escape codes removed.
    """
    return ansi_escape.sub("", text)
