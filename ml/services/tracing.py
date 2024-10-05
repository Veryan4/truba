from typing import Any
import contextvars
from opentracing import tags
from opentracing.propagation import Format
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
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


request_span = contextvars.ContextVar('request_span')


class OpentracingMiddleware(BaseHTTPMiddleware):

  @staticmethod
  def before_request(request: Request, tracer):
    """
        Gather various info about the request and start new span with the data.
        """
    span_context = tracer.extract(format=Format.HTTP_HEADERS,
                                  carrier=request.headers)
    span = tracer.start_span(
        operation_name=f"{request.method} {request.url.path}",
        child_of=span_context,
    )
    span.set_tag("http.url", str(request.url))

    remote_ip = request.client.host
    span.set_tag(tags.PEER_HOST_IPV4, remote_ip or "")

    remote_port = request.client.port
    span.set_tag(tags.PEER_PORT, remote_port or "")

    return span

  async def set_body(self, request: Request, body: bytes):

    async def receive():
      return {"type": "http.request", "body": body}

    request._receive = receive

  async def get_body(self, request: Request) -> bytes:
    body = await request.body()
    await self.set_body(request, body)
    return body

  async def dispatch(self, request: Request, call_next: Any) -> Response:
    """
        Store span in some request.state storage using Tracer.scope_manager,
        using the returned `Scope` as Context Manager to ensure
        `Span` will be cleared and (in this case) `Span.finish()` be called.
        :param request: Starlette's Request object
        :param call_next: Next callable Middleware in chain or final view
        :return: Starlette's Response object
        """

    if request.method == "POST":
      request.state.post = await self.get_body(request)
    if request.method == "PUT":
      request.state.put = await self.get_body(request)
    if request.method == "PATCH":
      request.state.patch = await self.get_body(request)

    tracer = request.app.tracer
    span = self.before_request(request, tracer)

    with tracer.scope_manager.activate(span, True) as scope:
      request_span.set(span)
      request.state.opentracing_span = span
      request.state.opentracing_scope = scope
      request.state.opentracing_tracer = tracer
      response = await call_next(request)
      return response
