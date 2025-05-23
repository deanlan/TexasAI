import asyncio
import inspect
import logging
from contextvars import ContextVar
from functools import wraps
from typing import Any, AsyncIterator, Dict, Optional

from texasgpt.component import ComponentType, SystemApp
from texasgpt.util.module_utils import import_from_checked_string
from texasgpt.util.tracer.base import (
    Span,
    SpanStorage,
    SpanStorageType,
    SpanType,
    Tracer,
    TracerContext,
)
from texasgpt.util.tracer.span_storage import MemorySpanStorage

logger = logging.getLogger(__name__)


class DefaultTracer(Tracer):
    def __init__(
        self,
        system_app: SystemApp | None = None,
        default_storage: SpanStorage = None,
        span_storage_type: SpanStorageType = SpanStorageType.ON_CREATE_END,
    ):
        super().__init__(system_app)
        self._span_stack_var = ContextVar("span_stack", default=[])

        if not default_storage:
            default_storage = MemorySpanStorage(system_app)
        self._default_storage = default_storage
        self._span_storage_type = span_storage_type

    def append_span(self, span: Span):
        self._get_current_storage().append_span(span.copy())

    def start_span(
        self,
        operation_name: str,
        parent_span_id: str = None,
        span_type: SpanType = None,
        metadata: Dict = None,
    ) -> Span:
        trace_id = (
            self._new_random_trace_id()
            if parent_span_id is None
            else parent_span_id.split(":")[0]
        )
        span_id = f"{trace_id}:{self._new_random_span_id()}"

        span = Span(
            trace_id,
            span_id,
            span_type,
            parent_span_id,
            operation_name,
            metadata=metadata,
        )

        if self._span_storage_type in [
            SpanStorageType.ON_END,
            SpanStorageType.ON_CREATE_END,
        ]:
            span.add_end_caller(self.append_span)

        if self._span_storage_type in [
            SpanStorageType.ON_CREATE,
            SpanStorageType.ON_CREATE_END,
        ]:
            self.append_span(span)
        current_stack = self._span_stack_var.get()
        current_stack.append(span)
        self._span_stack_var.set(current_stack)

        span.add_end_caller(self._remove_from_stack_top)
        return span

    def end_span(self, span: Span, **kwargs):
        """"""
        span.end(**kwargs)

    def _remove_from_stack_top(self, span: Span):
        current_stack = self._span_stack_var.get()
        if current_stack:
            current_stack.pop()
        self._span_stack_var.set(current_stack)

    def get_current_span(self) -> Optional[Span]:
        current_stack = self._span_stack_var.get()
        return current_stack[-1] if current_stack else None

    def _get_current_storage(self) -> SpanStorage:
        return self.system_app.get_component(
            ComponentType.TRACER_SPAN_STORAGE, SpanStorage, self._default_storage
        )


class TracerManager:
    """The manager of current tracer"""

    def __init__(self) -> None:
        self._system_app: Optional[SystemApp] = None
        self._trace_context_var: ContextVar[TracerContext] = ContextVar(
            "trace_context",
            default=TracerContext(),
        )

    def initialize(
        self, system_app: SystemApp, trace_context_var: ContextVar[TracerContext] = None
    ) -> None:
        self._system_app = system_app
        if trace_context_var:
            self._trace_context_var = trace_context_var

    def _get_tracer(self) -> Tracer:
        if not self._system_app:
            return None
        return self._system_app.get_component(ComponentType.TRACER, Tracer, None)

    def start_span(
        self,
        operation_name: str,
        parent_span_id: str = None,
        span_type: SpanType = None,
        metadata: Dict = None,
    ) -> Span:
        """Start a new span with operation_name
        This method must not throw an exception under any case and try not to block as much as possible
        """
        tracer = self._get_tracer()
        if not tracer:
            return Span(
                "empty_span", "empty_span", span_type=span_type, metadata=metadata
            )
        if not parent_span_id:
            parent_span_id = self.get_current_span_id()
        if not span_type and parent_span_id:
            span_type = self._get_current_span_type()
        return tracer.start_span(
            operation_name, parent_span_id, span_type=span_type, metadata=metadata
        )

    def end_span(self, span: Span, **kwargs):
        tracer = self._get_tracer()
        if not tracer or not span:
            return
        tracer.end_span(span, **kwargs)

    def get_current_span(self) -> Optional[Span]:
        tracer = self._get_tracer()
        if not tracer:
            return None
        return tracer.get_current_span()

    def get_current_span_id(self) -> Optional[str]:
        current_span = self.get_current_span()
        if current_span:
            return current_span.span_id
        ctx = self._trace_context_var.get()
        return ctx.span_id if ctx else None

    def _get_current_span_type(self) -> Optional[SpanType]:
        current_span = self.get_current_span()
        return current_span.span_type if current_span else None

    def _parse_span_id(self, body: Any) -> Optional[str]:
        from .base import _parse_span_id

        return _parse_span_id(body)

    def wrapper_async_stream(
        self,
        generator: AsyncIterator[Any],
        operation_name: str,
        parent_span_id: str = None,
        span_type: SpanType = None,
        metadata: Dict = None,
    ) -> AsyncIterator[Any]:
        """Wrap an async generator with a span"""

        parent_span_id = parent_span_id or self.get_current_span_id()

        async def wrapper():
            span = self.start_span(operation_name, parent_span_id, span_type, metadata)
            try:
                async for item in generator:
                    yield item
            finally:
                span.end()

        return wrapper()


root_tracer: TracerManager = TracerManager()


def trace(operation_name: Optional[str] = None, **trace_kwargs):
    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = (
                operation_name if operation_name else _parse_operation_name(func, *args)
            )
            with root_tracer.start_span(name, **trace_kwargs):
                return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = (
                operation_name if operation_name else _parse_operation_name(func, *args)
            )
            with root_tracer.start_span(name, **trace_kwargs):
                return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def _parse_operation_name(func, *args):
    self_name = None
    if inspect.signature(func).parameters.get("self"):
        self_name = args[0].__class__.__name__
    func_name = func.__name__
    if self_name:
        return f"{self_name}.{func_name}"
    return func_name


def initialize_tracer(
    tracer_filename: str,
    root_operation_name: str = "DB-GPT-Webserver",
    system_app: Optional[SystemApp] = None,
    tracer_storage_cls: Optional[str] = None,
    create_system_app: bool = False,
    enable_open_telemetry: bool = False,
    otlp_endpoint: Optional[str] = None,
    otlp_insecure: Optional[bool] = None,
    otlp_timeout: Optional[int] = None,
):
    """Initialize the tracer with the given filename and system app."""
    from texasgpt.util.tracer.span_storage import FileSpanStorage, SpanStorageContainer

    if not system_app and create_system_app:
        system_app = SystemApp()
    if not system_app:
        return

    trace_context_var = ContextVar(
        "trace_context",
        default=TracerContext(),
    )
    tracer = DefaultTracer(system_app)

    storage_container = SpanStorageContainer(system_app)
    storage_container.append_storage(FileSpanStorage(tracer_filename))
    if enable_open_telemetry:
        from texasgpt.util.tracer.opentelemetry import OpenTelemetrySpanStorage

        storage_container.append_storage(
            OpenTelemetrySpanStorage(
                service_name=root_operation_name,
                otlp_endpoint=otlp_endpoint,
                otlp_insecure=otlp_insecure,
                otlp_timeout=otlp_timeout,
            )
        )

    if tracer_storage_cls:
        logger.info(f"Begin parse storage class {tracer_storage_cls}")
        storage = import_from_checked_string(tracer_storage_cls, SpanStorage)
        storage_container.append_storage(storage())

    system_app.register_instance(storage_container)
    system_app.register_instance(tracer)
    root_tracer.initialize(system_app, trace_context_var)
    if system_app.app:
        from texasgpt.util.tracer.tracer_middleware import TraceIDMiddleware

        system_app.app.add_middleware(
            TraceIDMiddleware,
            trace_context_var=trace_context_var,
            tracer=tracer,
            root_operation_name=root_operation_name,
        )
