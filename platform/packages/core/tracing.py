"""
OpenTelemetry tracing setup.

Call configure_tracing(endpoint) once at process startup (from core/main.py).
When endpoint is None (the default), no SDK is initialised and the OTel API
falls back to its built-in no-op tracer — zero overhead, no side effects.

When endpoint is set (STARCORE_OTLP_ENDPOINT env var), a BatchSpanProcessor
is wired to an OTLP/HTTP exporter targeting that endpoint. Any OTel-compatible
collector (Jaeger, Grafana Tempo, Honeycomb, etc.) can receive the spans.

Usage anywhere in the codebase:
    from core.tracing import get_tracer
    with get_tracer().start_as_current_span("my.operation") as span:
        span.set_attribute("key", "value")
        ...
"""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_TRACER_NAME = "starcore"
_SERVICE_NAME = "starcore-platform"
_SERVICE_VERSION = "0.5.0"


def configure_tracing(endpoint: str | None) -> None:
    """Activate the OTel SDK when *endpoint* is provided; otherwise keep the no-op tracer."""
    if not endpoint:
        return
    resource = Resource.create({SERVICE_NAME: _SERVICE_NAME, SERVICE_VERSION: _SERVICE_VERSION})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)


def get_tracer() -> trace.Tracer:
    return trace.get_tracer(_TRACER_NAME)
