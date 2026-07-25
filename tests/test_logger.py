"""
Tests for core.logger module-level setup.
"""

from core.logger import _sink_kwargs, app_logger


def test_app_logger_is_exported():
    assert app_logger is not None


def test_app_logger_can_log_without_error():
    app_logger.info("test log message from test suite")
    app_logger.warning("test warning")
    app_logger.debug("test debug")


def test_sink_kwargs_text_mode():
    kwargs = _sink_kwargs(log_json=False)
    assert kwargs["serialize"] is False
    assert kwargs["level"] == "INFO"


def test_sink_kwargs_json_mode():
    kwargs = _sink_kwargs(log_json=True)
    assert kwargs["serialize"] is True
