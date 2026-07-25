"""
Central logging

Configures the process-wide loguru sink used by every package (each simply
does `from loguru import logger`, since loguru's logger is a process-wide
singleton). Importing this module applies the configuration as a side
effect; import it early (see core/main.py and apps/cli/main.py) so the
sink is set up before anything else logs.
"""

from __future__ import annotations

import sys
from typing import Any

from loguru import logger

from core.config import get_settings


def _sink_kwargs(log_json: bool) -> dict[str, Any]:
    """Translate the log-format setting into loguru `add()` kwargs.

    Extracted as a standalone, settings-free function so the JSON/text
    branch is unit-testable without reconfiguring the real, global loguru
    sink (see tests/test_logger.py).
    """
    return {
        "level": "INFO",
        "enqueue": True,
        "backtrace": True,
        "diagnose": False,
        "serialize": log_json,
    }


logger.remove()
logger.add(sys.stdout, **_sink_kwargs(get_settings().log_json))

app_logger = logger
