"""
Central logging
"""

import sys

from loguru import logger

logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    enqueue=True,
    backtrace=True,
    diagnose=False,
)

app_logger = logger
