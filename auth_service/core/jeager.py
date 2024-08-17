from typing import Optional

from fastapi import FastAPI
from opentelemetry import trace, context as context_api
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor, Span
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from core.config import settings, request_id_ctx

tracer = trace.get_tracer(__name__)


class RequestIdSpanProcessor(SpanProcessor):

    def on_start(self, span: "Span", parent_context: Optional[context_api.Context] = None) -> None:
        super().on_start(span, parent_context)
        request_id = request_id_ctx.get()
        if request_id:
            span.set_attribute("http.request_id", request_id)


def configure_tracer(app: FastAPI) -> None:
    resource = Resource(attributes={
        SERVICE_NAME: settings.project_name
    })

    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(RequestIdSpanProcessor())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name='localhost',
                agent_port=6831,
            )
        )
    )

    FastAPIInstrumentor.instrument_app(app)
