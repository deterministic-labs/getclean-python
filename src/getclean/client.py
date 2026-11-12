"""The getclean client: the generated client (base_client.py) with the hand-written code on top.

What it adds, in this file and in _layer.py:
- the host from GETCLEAN_BASE_URL when no base url is given;
- on every call that may bill: the limits read first, one idempotency key for the call, which stands on any error it
  raises, and the timeout per attempt from the operation's own bound;
- upload_contents taking the document as a path, bytes or a readable stream, and the `wait` helper that follows the
  upload's job to the record;
- iter_section, the section pager;
- list_jobs and list_contents dropping repeats by id while they page.
"""

from __future__ import annotations

import datetime as dt
import inspect
import os
import time
import typing
import uuid

import httpx
from . import core
from ._layer import (
    OMIT,
    TIMEOUT_MARGIN_SECONDS,
    Timeouts,
    base_url_from_environment,
    billed,
    billed_async,
    document_part,
    error_for_problem,
    headers_only,
    helper_wait,
    refused_for_good,
    sent_list,
    sleep_seconds,
    sleep_seconds_async,
    with_idempotency_key,
    with_job,
    without_repeats,
    without_repeats_async,
)
from .base_client import AsyncBaseGetClean, BaseGetClean
from .core.logging import LogConfig, Logger
from .core.pagination import AsyncPager, SyncPager
from .core.request_options import RequestOptions
from .environment import GetCleanEnvironment
from .errors.job_canceled import JobCanceled
from .raw_base_client import AsyncRawBaseGetClean, RawBaseGetClean
from .types.contents_compact import ContentsCompact
from .types.contents_page import ContentsPage
from .types.contents_upload import ContentsUpload
from .types.job import Job
from .types.job_page import JobPage
from .types.money import Money
from .types.retention import Retention
from .types.scope import Scope
from .types.section_contents import SectionContents

JOB_POLL_WAIT_SECONDS = 60.0
"""The wait helper asks get_job to hold the answer up to a minute at a time."""

CANCELED_STATE = "canceled"

DocumentInput = typing.Union[str, os.PathLike[str], core.File]
"""A document as this client takes it: the path of a file, or what the generated client takes (bytes, a stream, a
tuple).

Written without a forward reference, so a caller's module resolves it without importing os itself."""

RAW_RESPONSE_DOC = """The same client with each method returning the raw HTTP response.

The parsed answer is `data` beside the status and the headers. The raw client has none of this client's additions: no
limits read, no timeout per attempt, no `wait` and no repeat filter; a call that may bill carries the key you give it,
or one the client makes for that call. A list operation returns the pager itself, whose `response` is the page with
its `request_id`; the headers of a page are not carried."""


class GetClean(BaseGetClean):
    """The getclean client.

    getclean is the data layer for research agents: web pages and documents as clean, exact text with the facts of their
    source, and a search across the web and specialist sources with a receipt of what ran, every record saying what
    happened and every billed answer what it cost.

    The credential is `api_key`: an API key or an access token, as a value or as a function that returns one; when none
    is given, the environment variable GETCLEAN_API_KEY. A client built with neither raises ConfigurationError before
    any request leaves. The host is https://api.getclean.ai, or `base_url`, or the environment variable
    GETCLEAN_BASE_URL.

    A fetch or a search that did not deliver is an answer, not an error: its `outcome` says what happened. An HTTP
    refusal is a typed error, one class per status (getclean.errors), each carrying the problem as `body`; a job
    canceled before a record was made raises JobCanceled. A call that may bill carries one idempotency key for all its
    attempts, which stands on any error it raises as `idempotency_key`; the client retries 429, 502, 503, 504 and a 409
    whose problem type is idempotency-key-in-flight, five attempts in all with the same key, `max_retries` changing the
    count. The timeout of an attempt, which bounds each of its phases, connecting, writing, reading and waiting for the
    pool, is the operation's own bound from the limits plus ten seconds for a call that may bill, 120 seconds for a free
    call and until the limits are read; a timeout you set on the call or on the client stands.

    Examples
    --------
    with GetClean() as client:
        contents = client.fetch_contents(url="https://example.com/article")
        if contents.outcome.kind == "delivered":
            print(contents.markdown)
    """

    def __init__(
        self,
        *,
        base_url: typing.Optional[str] = None,
        environment: GetCleanEnvironment = GetCleanEnvironment.PRODUCTION,
        api_key: typing.Optional[typing.Union[str, typing.Callable[[], str]]] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        app_info: typing.Optional[typing.Dict[str, str]] = None,
        timeout: typing.Optional[float] = None,
        max_retries: typing.Optional[int] = None,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.Client] = None,
        logging: typing.Optional[typing.Union[LogConfig, Logger]] = None,
    ):
        super().__init__(
            base_url=base_url_from_environment(base_url),
            environment=environment,
            api_key=api_key,
            headers=headers,
            app_info=app_info,
            timeout=timeout,
            max_retries=max_retries,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
            logging=logging,
        )
        self._layer_timeouts = Timeouts()
        # The timeout per attempt is set only where neither the client's construction nor the call set one: a timeout
        # given here, or an HTTP client of your own with its timeout, stands.
        self._layer_sets_timeout = timeout is None and httpx_client is None

    @property
    def with_raw_response(self) -> RawBaseGetClean:
        return super().with_raw_response

    def _layer_read_limits(self, request_options: typing.Optional[typing.Mapping[str, typing.Any]]) -> None:
        """Reads the limits before the first call that may bill, carrying that call's headers alone.

        A reading that fails never fails the call: it leaves the defaults and is tried again before the next call that
        may bill, except after a 401 or a 403, which would meet the same refusal for the client's life. Two first calls
        started at once each read the limits, a free GET."""
        if self._layer_timeouts.read or self._layer_timeouts.refused:
            return
        try:
            self._layer_timeouts.take(
                self.get_limits(
                    request_options=typing.cast(typing.Optional[RequestOptions], headers_only(request_options))
                )
            )
        except Exception as error:
            if refused_for_good(error):
                self._layer_timeouts.refuse()

    # The calls that may bill: one key per call, the timeout of the operation's bound, and the key on every error.
    fetch_contents = billed("contents")(BaseGetClean.fetch_contents)
    fetch_contents_batch = billed("contents", "batch_seconds")(BaseGetClean.fetch_contents_batch)
    highlight_contents = billed("contents")(BaseGetClean.highlight_contents)
    fill_schema = billed("contents")(BaseGetClean.fill_schema)
    summarize_contents = billed("contents")(BaseGetClean.summarize_contents)
    search = billed("search")(BaseGetClean.search)
    search_batch = billed("search", "batch_seconds")(BaseGetClean.search_batch)
    _upload_contents = billed("contents")(BaseGetClean.upload_contents)

    def upload_contents(
        self,
        *,
        idempotency_key: typing.Optional[str] = None,
        document: typing.Optional[DocumentInput] = OMIT,
        url: typing.Optional[str] = OMIT,
        captured_url: typing.Optional[str] = OMIT,
        captured_at: typing.Optional[dt.datetime] = OMIT,
        baseline_fingerprint: typing.Optional[str] = OMIT,
        max_characters: typing.Optional[int] = OMIT,
        formats: typing.Optional[typing.Sequence[str]] = OMIT,
        block_kinds: typing.Optional[typing.Sequence[str]] = OMIT,
        highlights: typing.Optional[typing.Sequence[str]] = OMIT,
        json_schema: typing.Optional[typing.Dict[str, typing.Any]] = OMIT,
        summary: typing.Optional[bool] = OMIT,
        deterministic_only: typing.Optional[bool] = OMIT,
        recognition_languages: typing.Optional[typing.Sequence[str]] = OMIT,
        wait_seconds: typing.Optional[float] = OMIT,
        max_cost: typing.Optional[Money] = OMIT,
        max_source_price: typing.Optional[Money] = OMIT,
        retention: typing.Optional[Retention] = OMIT,
        pinned_version: typing.Optional[str] = OMIT,
        run_id: typing.Optional[str] = OMIT,
        metadata: typing.Optional[typing.Dict[str, str]] = OMIT,
        wait: bool = False,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ContentsUpload:
        key = idempotency_key if idempotency_key is not None else str(uuid.uuid4())
        upload = self._upload_contents(
            idempotency_key=key,
            document=document_part(document),
            url=url,
            captured_url=captured_url,
            captured_at=captured_at,
            baseline_fingerprint=baseline_fingerprint,
            max_characters=max_characters,
            formats=formats,
            block_kinds=block_kinds,
            highlights=highlights,
            json_schema=json_schema,
            summary=summary,
            deterministic_only=deterministic_only,
            recognition_languages=recognition_languages,
            wait_seconds=wait_seconds,
            max_cost=max_cost,
            max_source_price=max_source_price,
            retention=retention,
            pinned_version=pinned_version,
            run_id=run_id,
            metadata=metadata,
            request_options=request_options,
        )
        if not wait or upload.job is None or upload.contents is not None:
            return upload
        try:
            return self._follow_job(
                upload,
                max_characters=max_characters,
                formats=formats,
                block_kinds=block_kinds,
                request_options=request_options,
            )
        except Exception as error:
            # The wait is part of the upload's call: every error it raises carries the key the upload sent.
            with_idempotency_key(error, key)
            raise

    def _follow_job(
        self,
        upload: ContentsUpload,
        *,
        max_characters: typing.Optional[int],
        formats: typing.Optional[typing.Sequence[str]],
        block_kinds: typing.Optional[typing.Sequence[str]],
        request_options: typing.Optional[RequestOptions],
    ) -> ContentsUpload:
        """Follows the upload's job to its end, then reads its record.

        The polls and the read carry the caller's headers alone, each poll under its own timeout, and a transient
        failure of either is tried again within the job bound."""
        job = typing.cast(Job, upload.job)
        deadline = time.monotonic() + self._layer_timeouts.job_seconds()
        headers = headers_only(request_options)
        # Each poll is one attempt: the runtime's own retries would wait inside the poll past the bound, so the waits
        # between tries are this helper's, each checked against the time that remains before it begins.
        poll_options = typing.cast(
            RequestOptions,
            {**(headers or {}), "timeout": JOB_POLL_WAIT_SECONDS + TIMEOUT_MARGIN_SECONDS, "max_retries": 0},
        )
        tries = 0
        while not job.finished and time.monotonic() < deadline:
            try:
                job = self.get_job(job.id, wait_seconds=JOB_POLL_WAIT_SECONDS, request_options=poll_options)
                tries = 0
            except Exception as error:
                tries = _try_again(error, job, tries, deadline)
        if not job.finished:
            return ContentsUpload(job=job, request_id=upload.request_id)
        if job.contents_id is None:
            if job.state == CANCELED_STATE:
                raise JobCanceled(job)
            if job.problem is not None:
                failure = error_for_problem(job.problem)
                with_job(failure, job)
                raise failure
            return ContentsUpload(job=job, request_id=upload.request_id)
        tries = 0
        while True:
            try:
                contents = self.get_contents(
                    job.contents_id,
                    max_characters=None if max_characters is OMIT else max_characters,
                    formats=sent_list(formats),
                    block_kinds=sent_list(block_kinds),
                    request_options=typing.cast(RequestOptions, {**(headers or {}), "max_retries": 0}),
                )
                break
            except Exception as error:
                tries = _try_again(error, job, tries, deadline)
        return ContentsUpload(contents=contents, job=job, request_id=upload.request_id)

    def iter_section(
        self,
        contents_id: str,
        section_id: str,
        *,
        max_characters: typing.Optional[int] = None,
        scope: typing.Optional[Scope] = None,
        formats: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
        block_kinds: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
        page_token: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Iterator[SectionContents]:
        """Every page of a section in turn, from get_section (the docstring is composed below from get_section's)."""
        token = page_token
        while True:
            page = self.get_section(
                contents_id,
                section_id,
                max_characters=max_characters,
                scope=scope,
                formats=formats,
                block_kinds=block_kinds,
                page_token=token,
                request_options=request_options,
            )
            yield page
            token = page.next_page_token
            if token is None:
                return

    def list_jobs(
        self,
        *,
        state: typing.Optional[str] = None,
        kind: typing.Optional[str] = None,
        page_size: typing.Optional[int] = None,
        page_token: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[Job, JobPage]:
        return without_repeats(
            super().list_jobs(
                state=state, kind=kind, page_size=page_size, page_token=page_token, request_options=request_options
            )
        )

    def list_contents(
        self,
        *,
        url: typing.Optional[str] = None,
        carrier: typing.Optional[str] = None,
        run_id: typing.Optional[str] = None,
        page_size: typing.Optional[int] = None,
        page_token: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SyncPager[ContentsCompact, ContentsPage]:
        return without_repeats(
            super().list_contents(
                url=url,
                carrier=carrier,
                run_id=run_id,
                page_size=page_size,
                page_token=page_token,
                request_options=request_options,
            )
        )


class AsyncGetClean(AsyncBaseGetClean):
    """The getclean client for asyncio: every call is awaited.

    getclean is the data layer for research agents: web pages and documents as clean, exact text with the facts of their
    source, and a search across the web and specialist sources with a receipt of what ran, every record saying what
    happened and every billed answer what it cost.

    The credential is `api_key`: an API key or an access token, as a value or as a function that returns one, or
    `async_token`, an async function; when none is given, the environment variable GETCLEAN_API_KEY. A client built with
    neither raises ConfigurationError before any request leaves. The host is https://api.getclean.ai, or `base_url`, or
    the environment variable GETCLEAN_BASE_URL.

    A fetch or a search that did not deliver is an answer, not an error: its `outcome` says what happened. An HTTP
    refusal is a typed error, one class per status (getclean.errors), each carrying the problem as `body`; a job
    canceled before a record was made raises JobCanceled. A call that may bill carries one idempotency key for all its
    attempts, which stands on any error it raises as `idempotency_key`; the client retries 429, 502, 503, 504 and a 409
    whose problem type is idempotency-key-in-flight, five attempts in all with the same key, `max_retries` changing the
    count. The timeout of an attempt, which bounds each of its phases, connecting, writing, reading and waiting for the
    pool, is the operation's own bound from the limits plus ten seconds for a call that may bill, 120 seconds for a free
    call and until the limits are read; a timeout you set on the call or on the client stands.

    Examples
    --------
    async with AsyncGetClean() as client:
        contents = await client.fetch_contents(url="https://example.com/article")
        if contents.outcome.kind == "delivered":
            print(contents.markdown)
    """

    def __init__(
        self,
        *,
        base_url: typing.Optional[str] = None,
        environment: GetCleanEnvironment = GetCleanEnvironment.PRODUCTION,
        api_key: typing.Optional[typing.Union[str, typing.Callable[[], str]]] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        app_info: typing.Optional[typing.Dict[str, str]] = None,
        async_token: typing.Optional[typing.Callable[[], typing.Awaitable[str]]] = None,
        timeout: typing.Optional[float] = None,
        max_retries: typing.Optional[int] = None,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.AsyncClient] = None,
        logging: typing.Optional[typing.Union[LogConfig, Logger]] = None,
    ):
        super().__init__(
            base_url=base_url_from_environment(base_url),
            environment=environment,
            api_key=api_key,
            headers=headers,
            app_info=app_info,
            async_token=async_token,
            timeout=timeout,
            max_retries=max_retries,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
            logging=logging,
        )
        self._layer_timeouts = Timeouts()
        self._layer_sets_timeout = timeout is None and httpx_client is None

    @property
    def with_raw_response(self) -> AsyncRawBaseGetClean:
        return super().with_raw_response

    async def _layer_read_limits(self, request_options: typing.Optional[typing.Mapping[str, typing.Any]]) -> None:
        """The async form of GetClean._layer_read_limits."""
        if self._layer_timeouts.read or self._layer_timeouts.refused:
            return
        try:
            self._layer_timeouts.take(
                await self.get_limits(
                    request_options=typing.cast(typing.Optional[RequestOptions], headers_only(request_options))
                )
            )
        except Exception as error:
            if refused_for_good(error):
                self._layer_timeouts.refuse()

    fetch_contents = billed_async("contents")(AsyncBaseGetClean.fetch_contents)
    fetch_contents_batch = billed_async("contents", "batch_seconds")(AsyncBaseGetClean.fetch_contents_batch)
    highlight_contents = billed_async("contents")(AsyncBaseGetClean.highlight_contents)
    fill_schema = billed_async("contents")(AsyncBaseGetClean.fill_schema)
    summarize_contents = billed_async("contents")(AsyncBaseGetClean.summarize_contents)
    search = billed_async("search")(AsyncBaseGetClean.search)
    search_batch = billed_async("search", "batch_seconds")(AsyncBaseGetClean.search_batch)
    _upload_contents = billed_async("contents")(AsyncBaseGetClean.upload_contents)

    async def upload_contents(
        self,
        *,
        idempotency_key: typing.Optional[str] = None,
        document: typing.Optional[DocumentInput] = OMIT,
        url: typing.Optional[str] = OMIT,
        captured_url: typing.Optional[str] = OMIT,
        captured_at: typing.Optional[dt.datetime] = OMIT,
        baseline_fingerprint: typing.Optional[str] = OMIT,
        max_characters: typing.Optional[int] = OMIT,
        formats: typing.Optional[typing.Sequence[str]] = OMIT,
        block_kinds: typing.Optional[typing.Sequence[str]] = OMIT,
        highlights: typing.Optional[typing.Sequence[str]] = OMIT,
        json_schema: typing.Optional[typing.Dict[str, typing.Any]] = OMIT,
        summary: typing.Optional[bool] = OMIT,
        deterministic_only: typing.Optional[bool] = OMIT,
        recognition_languages: typing.Optional[typing.Sequence[str]] = OMIT,
        wait_seconds: typing.Optional[float] = OMIT,
        max_cost: typing.Optional[Money] = OMIT,
        max_source_price: typing.Optional[Money] = OMIT,
        retention: typing.Optional[Retention] = OMIT,
        pinned_version: typing.Optional[str] = OMIT,
        run_id: typing.Optional[str] = OMIT,
        metadata: typing.Optional[typing.Dict[str, str]] = OMIT,
        wait: bool = False,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ContentsUpload:
        key = idempotency_key if idempotency_key is not None else str(uuid.uuid4())
        upload = await self._upload_contents(
            idempotency_key=key,
            document=document_part(document),
            url=url,
            captured_url=captured_url,
            captured_at=captured_at,
            baseline_fingerprint=baseline_fingerprint,
            max_characters=max_characters,
            formats=formats,
            block_kinds=block_kinds,
            highlights=highlights,
            json_schema=json_schema,
            summary=summary,
            deterministic_only=deterministic_only,
            recognition_languages=recognition_languages,
            wait_seconds=wait_seconds,
            max_cost=max_cost,
            max_source_price=max_source_price,
            retention=retention,
            pinned_version=pinned_version,
            run_id=run_id,
            metadata=metadata,
            request_options=request_options,
        )
        if not wait or upload.job is None or upload.contents is not None:
            return upload
        try:
            return await self._follow_job(
                upload,
                max_characters=max_characters,
                formats=formats,
                block_kinds=block_kinds,
                request_options=request_options,
            )
        except Exception as error:
            with_idempotency_key(error, key)
            raise

    async def _follow_job(
        self,
        upload: ContentsUpload,
        *,
        max_characters: typing.Optional[int],
        formats: typing.Optional[typing.Sequence[str]],
        block_kinds: typing.Optional[typing.Sequence[str]],
        request_options: typing.Optional[RequestOptions],
    ) -> ContentsUpload:
        """The async form of GetClean._follow_job."""
        job = typing.cast(Job, upload.job)
        deadline = time.monotonic() + self._layer_timeouts.job_seconds()
        headers = headers_only(request_options)
        # Each poll is one attempt: the runtime's own retries would wait inside the poll past the bound, so the waits
        # between tries are this helper's, each checked against the time that remains before it begins.
        poll_options = typing.cast(
            RequestOptions,
            {**(headers or {}), "timeout": JOB_POLL_WAIT_SECONDS + TIMEOUT_MARGIN_SECONDS, "max_retries": 0},
        )
        tries = 0
        while not job.finished and time.monotonic() < deadline:
            try:
                job = await self.get_job(job.id, wait_seconds=JOB_POLL_WAIT_SECONDS, request_options=poll_options)
                tries = 0
            except Exception as error:
                tries = await _try_again_async(error, job, tries, deadline)
        if not job.finished:
            return ContentsUpload(job=job, request_id=upload.request_id)
        if job.contents_id is None:
            if job.state == CANCELED_STATE:
                raise JobCanceled(job)
            if job.problem is not None:
                failure = error_for_problem(job.problem)
                with_job(failure, job)
                raise failure
            return ContentsUpload(job=job, request_id=upload.request_id)
        tries = 0
        while True:
            try:
                contents = await self.get_contents(
                    job.contents_id,
                    max_characters=None if max_characters is OMIT else max_characters,
                    formats=sent_list(formats),
                    block_kinds=sent_list(block_kinds),
                    request_options=typing.cast(RequestOptions, {**(headers or {}), "max_retries": 0}),
                )
                break
            except Exception as error:
                tries = await _try_again_async(error, job, tries, deadline)
        return ContentsUpload(contents=contents, job=job, request_id=upload.request_id)

    async def iter_section(
        self,
        contents_id: str,
        section_id: str,
        *,
        max_characters: typing.Optional[int] = None,
        scope: typing.Optional[Scope] = None,
        formats: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
        block_kinds: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
        page_token: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.AsyncIterator[SectionContents]:
        """The async form of GetClean.iter_section (the docstring is composed below from get_section's)."""
        token = page_token
        while True:
            page = await self.get_section(
                contents_id,
                section_id,
                max_characters=max_characters,
                scope=scope,
                formats=formats,
                block_kinds=block_kinds,
                page_token=token,
                request_options=request_options,
            )
            yield page
            token = page.next_page_token
            if token is None:
                return

    async def list_jobs(
        self,
        *,
        state: typing.Optional[str] = None,
        kind: typing.Optional[str] = None,
        page_size: typing.Optional[int] = None,
        page_token: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[Job, JobPage]:
        return without_repeats_async(
            await super().list_jobs(
                state=state, kind=kind, page_size=page_size, page_token=page_token, request_options=request_options
            )
        )

    async def list_contents(
        self,
        *,
        url: typing.Optional[str] = None,
        carrier: typing.Optional[str] = None,
        run_id: typing.Optional[str] = None,
        page_size: typing.Optional[int] = None,
        page_token: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncPager[ContentsCompact, ContentsPage]:
        return without_repeats_async(
            await super().list_contents(
                url=url,
                carrier=carrier,
                run_id=run_id,
                page_size=page_size,
                page_token=page_token,
                request_options=request_options,
            )
        )


def _try_again(error: Exception, job: Job, tries: int, deadline: float) -> int:
    """Waits before the wait helper tries a poll or the read again after a transient failure, within the job bound.

    A failure that ends the helper, or one met at the bound, is raised with the last job seen on it."""
    wait = helper_wait(error, tries)
    if wait is None or time.monotonic() + wait > deadline:
        with_job(error, job)
        raise error
    sleep_seconds(wait)
    return tries + 1


async def _try_again_async(error: Exception, job: Job, tries: int, deadline: float) -> int:
    """The async form of _try_again."""
    wait = helper_wait(error, tries)
    if wait is None or time.monotonic() + wait > deadline:
        with_job(error, job)
        raise error
    await sleep_seconds_async(wait)
    return tries + 1


# The hand-written methods carry the operation's description first, as the generated base writes it from the
# contract, then this client's own paragraph, then the generated sections, with `wait` among the parameters where the
# method takes it; composed at import, so the text never drifts from the contract.
UPLOAD_LAYER_DOC = """What this client adds. `document` takes the path of a file (a `str` or `os.PathLike`: the file at
that path, sent under its base name), bytes, or a readable stream, which is read into memory once before the first
attempt, beside the tuple forms the base client takes; a path that names no file raises FileNotFoundError before any
request leaves. `wait` is off by default (False), and the answer comes as the wire gives it: `contents` with its `cost`
on a 201, which comes back as answered, `job` on a 202. With `wait=True` the call follows a 202's job to its end: the
job is polled up to a minute at a time, each poll under a timeout of its own and carrying your headers, until it is
final or the job bound and one more minute have passed, the bound being the limits' contents `job_seconds`, 30 minutes
until the limits are read; then the record is read under this call's `max_characters` and the lists it sent among
`formats` and `block_kinds`, carrying your headers as well, and ContentsUpload comes back with `contents` and the final
`job`, whose `cost` is the bill. The polls and the read carry none of the upload's query, body or timeout options. A
poll or the read that fails with a 429, a 5xx or no answer is tried again within the bound, after the server's wait or a
backoff from one second; a 4xx ends the call with that error. A job that failed with no record raises the error class of
its problem's status; a job canceled with no record raises JobCanceled; a job still running at the bound is returned as
it stands, for the caller to decide. Every error the wait raises carries the last job seen as `job` and the key the
upload sent as `idempotency_key`."""

WAIT_PARAMETER_DOC = """wait : bool
    Follow a 202's job to its end and read its record, as the paragraph above says. Default False."""

REPEATS_LAYER_DOC = """What this client adds. The list grows while it pages, so an item may reappear on a later page;
this pager drops an item whose `id` was already seen, page after page."""

SECTION_PAGER_DOC = """Every page of a section in turn, from get_section.

The pages run from the first page, or from `page_token` when you give one, to the last page, which carries no
next_page_token; each page is asked with your parameters and the token of the page before it."""

SECTION_PAGER_RETURNS = """{iterator}
    Every page of the section in turn, each a `SectionContents`: the record's facts, the section's row, its text in the
    formats asked for, and `next_page_token` on every page but the last."""

SECTION_PAGER_EXAMPLE = """from getclean import GetClean

client = GetClean()
for page in client.iter_section(
    contents_id="cnt_3Fk9abaUhNX7t2eKkgfd3e",
    section_id="s2",
    formats=["markdown"],
):
    print(page.markdown)"""

SECTION_PAGER_EXAMPLE_ASYNC = """import asyncio

from getclean import AsyncGetClean

client = AsyncGetClean()


async def main() -> None:
    async for page in client.iter_section(
        contents_id="cnt_3Fk9abaUhNX7t2eKkgfd3e",
        section_id="s2",
        formats=["markdown"],
    ):
        print(page.markdown)


asyncio.run(main())"""

_SECTION_HEADERS = ("Parameters", "Returns", "Raises", "Yields", "Examples")


def _sections(doc: str) -> typing.Tuple[str, typing.List[typing.Tuple[str, str]]]:
    """Splits a numpydoc docstring into its description and its sections, each a header with its body."""
    lines = inspect.cleandoc(doc).split("\n")
    starts = [
        i
        for i, line in enumerate(lines)
        if line.strip() in _SECTION_HEADERS and i + 1 < len(lines) and set(lines[i + 1].strip()) == {"-"}
    ]
    description = "\n".join(lines[: starts[0]] if starts else lines).strip()
    sections = []
    for n, start in enumerate(starts):
        stop = starts[n + 1] if n + 1 < len(starts) else len(lines)
        sections.append((lines[start].strip(), "\n".join(lines[start + 2 : stop]).strip()))
    return description, sections


def _compose_doc(
    generated: typing.Any,
    *,
    description: typing.Optional[str] = None,
    addition: typing.Optional[str] = None,
    parameter: typing.Optional[str] = None,
    returns: typing.Optional[str] = None,
    examples: typing.Optional[str] = None,
) -> str:
    """The docstring of a hand-written method, composed from the generated one.

    Its description (or the one given), the addition after it, and its sections: a parameter added before
    request_options, the Returns and the Examples replaced where given.
    """
    generated_description, sections = _sections(generated.__doc__ or "")
    parts = [description or generated_description]
    if addition:
        parts.append(addition)
    for header, body in sections:
        if header == "Parameters" and parameter:
            body = body.replace("request_options : ", f"{parameter}\n\nrequest_options : ", 1)
        elif header == "Returns" and returns:
            body = returns
        elif header == "Examples" and examples:
            body = examples
        parts.append(f"{header}\n{'-' * len(header)}\n{body}")
    return "\n\n".join(parts)


for _client, _base in ((GetClean, BaseGetClean), (AsyncGetClean, AsyncBaseGetClean)):
    _client.upload_contents.__doc__ = _compose_doc(
        _base.upload_contents, addition=UPLOAD_LAYER_DOC, parameter=WAIT_PARAMETER_DOC
    )
    _client.list_jobs.__doc__ = _compose_doc(_base.list_jobs, addition=REPEATS_LAYER_DOC)
    _client.list_contents.__doc__ = _compose_doc(_base.list_contents, addition=REPEATS_LAYER_DOC)
    _client.with_raw_response.__doc__ = RAW_RESPONSE_DOC
GetClean.iter_section.__doc__ = _compose_doc(
    BaseGetClean.get_section,
    description=SECTION_PAGER_DOC,
    returns=SECTION_PAGER_RETURNS.format(iterator="typing.Iterator[SectionContents]"),
    examples=SECTION_PAGER_EXAMPLE,
)
AsyncGetClean.iter_section.__doc__ = _compose_doc(
    AsyncBaseGetClean.get_section,
    description=SECTION_PAGER_DOC,
    returns=SECTION_PAGER_RETURNS.format(iterator="typing.AsyncIterator[SectionContents]"),
    examples=SECTION_PAGER_EXAMPLE_ASYNC,
)

__all__ = ["AsyncGetClean", "DocumentInput", "GetClean", "JobCanceled"]
