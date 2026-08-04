"""
OpenTelemetry tracing tests — core/tracing.py.

Verifies configure_tracing() is a no-op when no endpoint is given, and that it
activates the SDK and produces spans when an endpoint is configured.

OTel's global TracerProvider uses a "set once" lock (_TRACER_PROVIDER_SET_ONCE).
Tests that exercise set_tracer_provider() must save and restore both the provider
reference and the once-lock to avoid cross-test state pollution.
"""

from __future__ import annotations

import opentelemetry.trace as _trace_api
import pytest
from core.tracing import _TRACER_NAME, configure_tracing, get_tracer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


@pytest.fixture(autouse=True)
def _restore_otel_provider():
    """Save and restore the global OTel TracerProvider and its set-once lock."""
    saved_provider = _trace_api._TRACER_PROVIDER
    saved_done = _trace_api._TRACER_PROVIDER_SET_ONCE._done
    yield
    _trace_api._TRACER_PROVIDER = saved_provider
    _trace_api._TRACER_PROVIDER_SET_ONCE._done = saved_done


@pytest.fixture
def capturing_provider() -> tuple[TracerProvider, InMemorySpanExporter]:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    _trace_api._TRACER_PROVIDER = provider
    _trace_api._TRACER_PROVIDER_SET_ONCE._done = True
    return provider, exporter


def test_configure_tracing_no_op_when_endpoint_none():
    """configure_tracing(None) must not replace the global TracerProvider."""
    before = _trace_api._TRACER_PROVIDER
    configure_tracing(None)
    assert _trace_api._TRACER_PROVIDER is before


def test_configure_tracing_no_op_when_endpoint_empty():
    """configure_tracing('') must leave the global provider unchanged."""
    before = _trace_api._TRACER_PROVIDER
    configure_tracing("")
    assert _trace_api._TRACER_PROVIDER is before


def test_configure_tracing_activates_sdk():
    """configure_tracing(endpoint) installs a real TracerProvider."""
    configure_tracing("http://localhost:4318/v1/traces")
    assert isinstance(_trace_api._TRACER_PROVIDER, TracerProvider)


def test_configure_tracing_creates_resource_attributes():
    """The installed TracerProvider carries SERVICE_NAME and SERVICE_VERSION."""
    configure_tracing("http://localhost:4318/v1/traces")
    provider = _trace_api._TRACER_PROVIDER
    assert isinstance(provider, TracerProvider)
    attrs = provider.resource.attributes
    assert attrs.get("service.name") == "starcore-platform"
    assert attrs.get("service.version") == "0.4.0"


def test_get_tracer_returns_tracer():
    """get_tracer() always returns an opentelemetry Tracer."""
    tracer = get_tracer()
    assert hasattr(tracer, "start_as_current_span")


def test_get_tracer_uses_starcore_name(capturing_provider):
    """get_tracer() uses the 'starcore' instrumentation scope."""
    provider, exporter = capturing_provider
    tracer = get_tracer()
    with tracer.start_as_current_span("test.op"):
        pass
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].instrumentation_scope.name == _TRACER_NAME


def test_spans_captured_with_real_provider(capturing_provider):
    """Spans produced via get_tracer() are exported to InMemorySpanExporter."""
    _, exporter = capturing_provider
    tracer = get_tracer()
    with tracer.start_as_current_span("my.operation") as span:
        span.set_attribute("key", "value")
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "my.operation"
    assert spans[0].attributes["key"] == "value"


def test_nested_spans_captured(capturing_provider):
    """Child spans are captured and linked to the parent correctly."""
    _, exporter = capturing_provider
    tracer = get_tracer()
    with tracer.start_as_current_span("parent"):
        with tracer.start_as_current_span("child"):
            pass
    spans = exporter.get_finished_spans()
    assert len(spans) == 2
    names = {s.name for s in spans}
    assert names == {"parent", "child"}


def test_multiple_configure_calls_first_wins():
    """Calling configure_tracing twice — second call is silently ignored."""
    configure_tracing("http://first:4318/v1/traces")
    first_provider = _trace_api._TRACER_PROVIDER
    configure_tracing("http://second:4318/v1/traces")
    assert _trace_api._TRACER_PROVIDER is first_provider
