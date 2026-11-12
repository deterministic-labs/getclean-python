"""The hand-written part of the getclean Python SDK: what the generated client cannot do from the contract alone.

The client classes in client.py use these pieces:

- on every call that may bill: the limits read first, one idempotency key for the call, carried on every attempt and
  left on any error the call raises, and the timeout per attempt, the operation's own bound from the limits plus ten
  seconds, 120 seconds until the limits are read, set only where neither the call nor the client's construction set one;
- a document given as a path, bytes or a readable stream, a stream read into memory once before the first attempt;
- the waits of the upload's wait helper between its tries of a poll or the read after a transient failure;
- the pagers of list_jobs and list_contents dropping repeats by id, since those lists grow while they page;
- the error class a job's problem is raised as.

The generated runtime retries 429, 502, 503, 504 and a 409 whose problem type is idempotency-key-in-flight under one
count of attempts; the hand-written code adds no retry of its own. The upload's wait helper and iter_section live in
client.py, on the client classes themselves.
"""

from __future__ import annotations

import asyncio
import functools
import os
import pathlib
import random
import time
import typing
import uuid

import httpx
import typing_extensions
from . import errors as _errors
from ._problem_types import PROBLEM_STATUS_BY_TYPE
from .core.api_error import ApiError
from .core.pagination import AsyncPager, SyncPager
from .types.limits import Limits
from .types.problem import Problem

TIMEOUT_UNTIL_LIMITS_READ_SECONDS = 120.0
TIMEOUT_MARGIN_SECONDS = 10.0
"""The timeout per attempt: the operation's own bound plus the margin; 120 seconds until get_limits is read."""

JOB_BOUND_UNTIL_LIMITS_READ_SECONDS = 1800.0
JOB_BOUND_MARGIN_SECONDS = 60.0
"""The wait helper gives a job the contents job_seconds bound and one more minute; 30 minutes until it is read."""

HELPER_BACKOFF_FIRST_SECONDS = 1.0
HELPER_BACKOFF_CAP_SECONDS = 30.0
"""The wait helper's wait before it tries a poll or the read again after a transient failure, each poll and the read
being one attempt: the server's wait when it sent one, else 1 second doubling each time, varied by up to 10 percent,
never past 30 seconds."""

REFUSED_FOR_THE_CLIENTS_LIFE = (401, 403)
"""A limits read answered with one of these is not repeated: the key is unknown, or lacks the scope, for good."""

OMIT: typing.Any = ...
"""The generated client's sentinel for an argument left out (base_client.py)."""

P = typing_extensions.ParamSpec("P")
R = typing.TypeVar("R")
T = typing.TypeVar("T")
S = typing.TypeVar("S")

Options = typing.Optional[typing.Mapping[str, typing.Any]]
"""Request options as the hand-written code reads them: the generated RequestOptions, a mapping, or none."""


class Timeouts:
    """The timeouts per operation, from the limits once they are read, and whether the limits can be read at all."""

    def __init__(self) -> None:
        self._limits: typing.Optional[Limits] = None
        self._refused = False

    @property
    def read(self) -> bool:
        return self._limits is not None

    @property
    def refused(self) -> bool:
        """Whether a limits read was refused for the client's life (a 401 or a 403), so it is not tried again."""
        return self._refused

    def take(self, limits: Limits) -> None:
        self._limits = limits

    def refuse(self) -> None:
        self._refused = True

    def _bound_max(self, family: str, name: str) -> typing.Optional[float]:
        if self._limits is None:
            return None
        bounds = getattr(self._limits.bounds, family, None)
        if not isinstance(bounds, dict):
            return None
        bound = bounds.get(name)
        if bound is None or bound.max is None:
            return None
        return float(bound.max)

    def seconds(self, family: str, bound: str) -> float:
        """The timeout of one attempt of a call timed by this bound of the family, call_seconds or batch_seconds.

        The bound plus the margin; 120 seconds until the limits are read, or when they lack the bound."""
        limit = self._bound_max(family, bound)
        if limit is None:
            return TIMEOUT_UNTIL_LIMITS_READ_SECONDS
        return limit + TIMEOUT_MARGIN_SECONDS

    def job_seconds(self) -> float:
        """The wait helper's bound: contents job_seconds plus a minute; 31 minutes until the limits are read."""
        bound = self._bound_max("contents", "job_seconds")
        if bound is None:
            return JOB_BOUND_UNTIL_LIMITS_READ_SECONDS + JOB_BOUND_MARGIN_SECONDS
        return bound + JOB_BOUND_MARGIN_SECONDS


class LayerClient(typing_extensions.Protocol):
    """What the billed-call decorators need of a client.

    Its timeouts, whether it sets the timeout per attempt at all, and the reading of the limits."""

    _layer_timeouts: Timeouts
    _layer_sets_timeout: bool

    def _layer_read_limits(self, request_options: Options) -> None: ...


class AsyncLayerClient(typing_extensions.Protocol):
    _layer_timeouts: Timeouts
    _layer_sets_timeout: bool

    async def _layer_read_limits(self, request_options: Options) -> None: ...


def headers_only(request_options: Options) -> typing.Optional[typing.Dict[str, typing.Any]]:
    """The caller's headers alone, as the request options of a call this client makes on the caller's behalf.

    The limits read, a poll and the record's read carry them; none of the call's query, body, timeout or retry options
    go with them."""
    if request_options is None or request_options.get("additional_headers") is None:
        return None
    return {"additional_headers": request_options["additional_headers"]}


def refused_for_good(error: BaseException) -> bool:
    """Whether a failed limits read is one that would fail again for the client's life."""
    return isinstance(error, ApiError) and error.status_code in REFUSED_FOR_THE_CLIENTS_LIFE


def with_key_and_timeout(
    kwargs: typing.Dict[str, typing.Any], timeout_seconds: typing.Optional[float]
) -> typing.Tuple[typing.Dict[str, typing.Any], str]:
    """The call's keyword arguments with one idempotency key and, where this client sets it, the timeout per attempt.

    The key comes back beside them, since it stands on every error the call raises. It is the caller's when given, else
    the same form the generated client makes for a call given none (core/idempotency.py, a UUID v4), made here so the
    hand-written code has it to leave on an error. The timeout bounds each attempt of the generated retries; one the
    caller set in the request options, `timeout` or `timeout_in_seconds`, stands, and None leaves the client's own.
    """
    prepared = dict(kwargs)
    key = prepared.get("idempotency_key")
    if key is None:
        key = str(uuid.uuid4())
        prepared["idempotency_key"] = key
    if timeout_seconds is not None:
        options = dict(prepared.get("request_options") or {})
        if options.get("timeout") is None and options.get("timeout_in_seconds") is None:
            options["timeout"] = timeout_seconds
        prepared["request_options"] = options
    return prepared, str(key)


def with_idempotency_key(error: BaseException, key: str) -> None:
    """Leaves the key the call carried on the error it raised, as `idempotency_key`, so a repeat is a replay."""
    setattr(error, "idempotency_key", key)


def with_job(error: BaseException, job: typing.Any) -> None:
    """Leaves the last job the wait helper saw on the error that ended it, as `job`, so the caller holds its id."""
    setattr(error, "job", job)


def billed(family: str, bound: str = "call_seconds") -> typing.Callable[[typing.Callable[P, R]], typing.Callable[P, R]]:
    """Wraps a generated method that may bill.

    The limits are read first; the call carries one key on every attempt and on every error it raises; the timeout per
    attempt comes from the bound that times the operation."""

    def decorate(method: typing.Callable[P, R]) -> typing.Callable[P, R]:
        @functools.wraps(method)
        def call(*args: P.args, **kwargs: P.kwargs) -> R:
            client = typing.cast(LayerClient, args[0])
            client._layer_read_limits(typing.cast(Options, kwargs.get("request_options")))
            timeout = client._layer_timeouts.seconds(family, bound) if client._layer_sets_timeout else None
            prepared, key = with_key_and_timeout(dict(kwargs), timeout)
            try:
                return method(*args, **typing.cast(typing.Any, prepared))
            except Exception as error:
                with_idempotency_key(error, key)
                raise

        return typing.cast(typing.Callable[P, R], call)

    return decorate


Coroutine = typing.Coroutine[typing.Any, typing.Any, R]


def billed_async(
    family: str, bound: str = "call_seconds"
) -> typing.Callable[[typing.Callable[P, Coroutine[R]]], typing.Callable[P, Coroutine[R]]]:
    """The async form of billed(); the methods stay coroutine functions for the type checker, as the base declares."""

    def decorate(method: typing.Callable[P, Coroutine[R]]) -> typing.Callable[P, Coroutine[R]]:
        @functools.wraps(method)
        async def call(*args: P.args, **kwargs: P.kwargs) -> R:
            client = typing.cast(AsyncLayerClient, args[0])
            await client._layer_read_limits(typing.cast(Options, kwargs.get("request_options")))
            timeout = client._layer_timeouts.seconds(family, bound) if client._layer_sets_timeout else None
            prepared, key = with_key_and_timeout(dict(kwargs), timeout)
            try:
                return await method(*args, **typing.cast(typing.Any, prepared))
            except Exception as error:
                with_idempotency_key(error, key)
                raise

        return typing.cast(typing.Callable[P, Coroutine[R]], call)

    return decorate


def document_part(document: typing.Any) -> typing.Any:
    """The document as the generated client takes it.

    A path becomes the file at that path, named by its base name; a readable stream is read into memory once, before the
    first attempt, so every attempt sends the same bytes; bytes and the tuple forms pass as they are, a stream inside
    the tuple read the same way."""
    if document is OMIT or document is None:
        return document
    if isinstance(document, (str, os.PathLike)):
        path = pathlib.Path(document)
        return (path.name, path.read_bytes())
    if hasattr(document, "read"):
        return document.read()
    if isinstance(document, tuple) and len(document) >= 2 and hasattr(document[1], "read"):
        return (document[0], document[1].read(), *document[2:])
    return document


def sent_list(value: typing.Any) -> typing.Optional[typing.List[typing.Any]]:
    """A list the upload sent, as the record's read after its job takes it.

    The list when it holds something, else None, since an empty list leaves a form and a query refuses one."""
    if value is OMIT or not value:
        return None
    return list(value)


def _retry_after_seconds(error: ApiError) -> typing.Optional[float]:
    """The wait the server asked for on a transient failure, from Retry-After, never below zero."""
    for name, value in (error.headers or {}).items():
        if name.lower() == "retry-after":
            try:
                return max(float(value), 0.0)
            except (TypeError, ValueError):
                return None
    return None


def helper_wait(error: BaseException, retries: int) -> typing.Optional[float]:
    """How long the wait helper waits before trying a poll or the read again, or None when the failure ends it.

    A 429, a 5xx or a transport failure of a poll or the read, each one attempt, is a transient failure of a free read
    that repeats without harm: the server's wait when it sent one, else the backoff with its jitter. Any other error,
    a 4xx among them, ends the helper as it arrived.
    """
    if isinstance(error, ApiError):
        status = error.status_code
        if status is None or (status != 429 and status < 500):
            return None
        asked = _retry_after_seconds(error)
        if asked is not None:
            return asked
    elif not isinstance(error, httpx.HTTPError):
        return None
    backoff = HELPER_BACKOFF_FIRST_SECONDS * (2.0**retries)
    return min(backoff * random.uniform(0.9, 1.1), HELPER_BACKOFF_CAP_SECONDS)


def sleep_seconds(seconds: float) -> None:
    time.sleep(seconds)


async def sleep_seconds_async(seconds: float) -> None:
    await asyncio.sleep(seconds)


def base_url_from_environment(base_url: typing.Optional[str]) -> typing.Optional[str]:
    """The base url given, else GETCLEAN_BASE_URL when it is set and not empty."""
    if base_url is not None:
        return base_url
    from_environment = os.getenv("GETCLEAN_BASE_URL")
    return from_environment if from_environment else None


@functools.lru_cache(maxsize=1)
def _error_class_by_status() -> typing.Dict[int, typing.Type[ApiError]]:
    """The generated error class of each status, read from the classes themselves."""
    by_status: typing.Dict[int, typing.Type[ApiError]] = {}
    for name in _errors.__all__:
        error_class = getattr(_errors, name)
        probe = error_class(body=None)
        if isinstance(probe, ApiError) and probe.status_code is not None:
            by_status[probe.status_code] = error_class
    return by_status


def problem_status(problem: Problem) -> typing.Optional[int]:
    """The problem's status: its own when it carries one, else the status the contract gives its type.

    A problem nested in a job carries no status (the contract's Problem schema); its type's last segment names the
    type, and _problem_types.py, derived from the contract's table at every build, gives the status.
    """
    if problem.status is not None:
        return problem.status
    return PROBLEM_STATUS_BY_TYPE.get(problem.type.rsplit("/", 1)[-1])


def error_for_problem(problem: Problem) -> ApiError:
    """A job's problem as the error class of its status, or the base error when the status names no class."""
    status = problem_status(problem)
    error_class = _error_class_by_status().get(status) if status is not None else None
    if error_class is None:
        return ApiError(status_code=status, body=problem)
    return error_class(body=problem)


def _ids_of(items: typing.Optional[typing.List[typing.Any]]) -> typing.Set[str]:
    return {item.id for item in items or [] if isinstance(getattr(item, "id", None), str)}


def _unseen(item: typing.Any, seen: typing.Set[str]) -> bool:
    key = getattr(item, "id", None)
    if not isinstance(key, str):
        return True
    if key in seen:
        return False
    seen.add(key)
    return True


def without_repeats(pager: SyncPager[T, S], seen: typing.Optional[typing.Set[str]] = None) -> SyncPager[T, S]:
    """The pager with every item whose id was already seen dropped, page after page.

    The first page is the wire's; the memory of what was seen belongs to one iteration, starting from that page each
    time the next page is asked for, so a pager iterated twice yields the same items twice. A later page whose every
    item was seen is passed over for the one after it, since the generated iteration ends at a page with no items
    (core/pagination.py, iter_pages); the pages the caller sees each hold something new, or are the last. Each page's
    `response` is the answer as the wire gave it.
    """
    seen_ids = seen
    items = pager.items if seen_ids is None else [item for item in pager.items or [] if _unseen(item, seen_ids)]
    if pager.items is None:
        items = None

    def next_page() -> typing.Optional[SyncPager[T, S]]:
        memory = _ids_of(pager.items) if seen_ids is None else seen_ids
        page = pager
        while page.get_next is not None:
            following = page.get_next()
            if following is None:
                return None
            filtered = without_repeats(following, memory)
            if filtered.items or not following.has_next:
                return filtered
            page = following
        return None

    return SyncPager(
        get_next=next_page if pager.get_next is not None else None,
        has_next=pager.has_next,
        items=items,
        response=pager.response,
    )


def without_repeats_async(pager: AsyncPager[T, S], seen: typing.Optional[typing.Set[str]] = None) -> AsyncPager[T, S]:
    """The async form of without_repeats()."""
    seen_ids = seen
    items = pager.items if seen_ids is None else [item for item in pager.items or [] if _unseen(item, seen_ids)]
    if pager.items is None:
        items = None

    async def next_page() -> typing.Optional[AsyncPager[T, S]]:
        memory = _ids_of(pager.items) if seen_ids is None else seen_ids
        page = pager
        while page.get_next is not None:
            following = await page.get_next()
            if following is None:
                return None
            filtered = without_repeats_async(following, memory)
            if filtered.items or not following.has_next:
                return filtered
            page = following
        return None

    return AsyncPager(
        get_next=next_page if pager.get_next is not None else None,
        has_next=pager.has_next,
        items=items,
        response=pager.response,
    )
