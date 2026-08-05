"""
Central logging

Configures the process-wide loguru sink used by every package (each simply
does `from loguru import logger`, since loguru's logger is a process-wide
singleton). Importing this module applies the configuration as a side
effect; import it early (see core/main.py and apps/cli/main.py) so the
sink is set up before anything else logs.

Every log record carries a `request_id` extra field, defaulting to `"-"`
for log calls made outside an HTTP request (CLI commands, startup,
background work). `core/main.py`'s request-ID middleware overrides it to
the current request's correlation ID for the duration of that request via
`logger.contextualize()`, whose context-manager-scoped binding is backed
by the same `contextvars` machinery Python's own `asyncio` uses -- so it
is automatically inherited by any coroutine awaited from within the
request (including a `Scheduler.execute()` wave), with no extra
propagation code needed.
"""

from __future__ import annotations

import sys
from typing import Any

from loguru import logger

from core.config import get_settings

_TEXT_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | "
    "<cyan>req={extra[request_id]}</cyan> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)


def _sink_kwargs(log_json: bool) -> dict[str, Any]:
    """Translate the log-format setting into loguru `add()` kwargs.

    Extracted as a standalone, settings-free function so the JSON/text
    branch is unit-testable without reconfiguring the real, global loguru
    sink (see tests/test_logger.py). JSON mode (`serialize=True`) needs no
    explicit `format`: loguru serializes the full record, `extra` (and
    therefore `request_id`) included, regardless of `format`. Text mode
    uses `_TEXT_FORMAT` so `request_id` is visible there too.
    """
    kwargs: dict[str, Any] = {
        "level": "INFO",
        "enqueue": True,
        "backtrace": True,
        "diagnose": False,
        "serialize": log_json,
    }
    if not log_json:
        kwargs["format"] = _TEXT_FORMAT
    return kwargs


logger.remove()
logger.configure(extra={"request_id": "-"})
logger.add(sys.stdout, **_sink_kwargs(get_settings().log_json))

app_logger = logger
