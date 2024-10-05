from jaeger_client import Config
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory
from opentracing.scope_managers.asyncio import AsyncioScopeManager
import os

service = os.getenv("ENVIRONMENT", "") + "_" + os.getenv("SERVICE_NAME", "")
config = Config(
    config={
        "local_agent": {
            "reporting_host": os.getenv("JAEGER_AGENT_HOSTNAME", ""),
            "reporting_port": os.getenv("JAEGER_AGENT_PORT", "")
        },
        "sampler": {
            "type": "probabilistic",
            "param": "1.0",
        },
        "trace_id_header": "X-TRACE-ID"
    },
    service_name=service,
    validate=True,
    #update 'namespace=' to 'service_name_label=' new pypi jaeger-client is released
    metrics_factory=PrometheusMetricsFactory(namespace=service),
    scope_manager=AsyncioScopeManager())
tracer = config.initialize_tracer()


def log(currentModule, traceType, messageToLog):
  span = tracer.start_span(currentModule)
  span.set_tag(traceType, messageToLog)
  span.finish()


def init_tracer(app):
  app.tracer = tracer
