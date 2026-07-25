"""
Tests for core.logger module-level setup.
"""

from core.logger import app_logger


def test_app_logger_is_exported():
    assert app_logger is not None


def test_app_logger_can_log_without_error():
    app_logger.info("test log message from test suite")
    app_logger.warning("test warning")
    app_logger.debug("test debug")
