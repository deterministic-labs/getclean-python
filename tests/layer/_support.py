"""What the client's tests share: a scripted server, the API's example bodies, and a stand-in for time.

No test reaches the network. Every request goes to a scripted server that answers in the order the test wrote and keeps
each request for the test to read. A request the script did not expect is kept apart and answered 421 Misdirected
Request, a status no operation of the API answers, so the client raises it and retries nothing; each test asserts after
its call that no such request came.

Every body the server answers with is one of the API's own examples, copied value for value from the contract into
api_examples.json, or one built from an example with the members a case needs changed, each change beside its reason,
so that every body is one the contract's schema takes; every answer carries the headers the contract requires of it.
No test sleeps: the clock and the two sleeps are replaced at their own modules, every wait the client asks for is
recorded and moves the clock instead of passing, and a random draw is pinned where a test reads a backoff.
"""

from __future__ import annotations

import asyncio
import copy
import decimal
import email.message
import inspect
import itertools
import json
import math
import pathlib
import random
import sys
import time
import typing

import httpx
import pytest

from getclean import AsyncGetClean, GetClean
from getclean.base_client import AsyncBaseGetClean, BaseGetClean
from getclean.core.pagination import AsyncPager
from getclean.types.contents_batch_item import ContentsBatchItem
from getclean.types.search_batch_item import SearchBatchItem

T = typing.TypeVar("T")
Body = typing.Dict[str, typing.Any]

BASE_URL = "http://getclean.test"
"""A host under the reserved .test domain. The scripted server answers every request, so none leaves the machine."""

CLIENT_TIMEOUT = httpx.Timeout(5.0)
"""The timeout of the HTTP client a test hands the SDK, 5 seconds: the caller's own, which the client never replaces."""

CLIENTS = pytest.mark.parametrize("client_class", [GetClean, AsyncGetClean], ids=["GetClean", "AsyncGetClean"])
"""Runs a test once on each client."""


# --- the API's own examples


EXAMPLES: typing.Dict[str, typing.Any] = json.loads(
    pathlib.Path(__file__).with_name("api_examples.json").read_text(encoding="utf-8")
)
"""The API's named answer examples, each under its name in the contract, value for value."""


def example(name: str) -> typing.Any:
    """A fresh copy of the API's example of this name, for a test to change."""
    return copy.deepcopy(EXAMPLES[name])


_ANSWER_NUMBERS = itertools.count(1)


def request_id(label: str = "") -> str:
    """A request id of the contract's form, req_ and 22 letters or digits. A label names the answer the id marks; with
    no label the id is a fresh one, since every call has an id of its own."""
    label = label or f"Answer{next(_ANSWER_NUMBERS)}"
    assert label.isalnum() and len(label) <= 22, f"a request id's label is up to 22 letters or digits: {label!r}"
    return "req_" + label.ljust(22, "x")


def under_request_id(body: T, new_id: str) -> T:
    """The body as the answer of another call: every member that repeats the call's request id, the nested records' and
    the nested problems' instance URLs among them, carries the new id."""
    old_id = typing.cast(Body, body)["request_id"]
    return typing.cast(T, json.loads(json.dumps(body).replace(old_id, new_id)))


PRICES: Body = EXAMPLES["get_limits.limits"]["prices"]
"""The prices of the limits example, by unit."""


def money(amount: typing.Union[str, decimal.Decimal]) -> Body:
    """A sum of the contract's form: the amount as a decimal string with four fraction digits, in the account's USD."""
    return {"amount": f"{decimal.Decimal(amount):.4f}", "currency": "USD"}


def price(unit: str) -> decimal.Decimal:
    return decimal.Decimal(PRICES[unit]["amount"])


# --- problems


PROBLEM_TYPE_BASE = "https://api.getclean.ai/problems/"
"""Where every problem type's URI begins (the contract, Problem.type)."""

PROBLEM_TABLE: typing.Dict[str, typing.Tuple[int, str, str]] = {
    # Each problem type with its status, who must act and its title, as the table under Problem.type in the API's
    # contract gives them. "caller, after the wait" is the caller; insufficient-scope is the account owner's move for an
    # API key, the credential these tests use.
    "invalid-request": (400, "caller", "The request is invalid"),
    "page-token-invalid": (400, "caller", "The page token is invalid"),
    "unauthorized": (401, "caller", "The key is missing or rejected"),
    "insufficient-scope": (403, "account_owner", "The key lacks a scope this call needs"),
    "policy-limit-exceeded": (403, "account_owner", "The key's policy forbids this"),
    "datasource-access-required": (403, "account_owner", "The datasource needs a registered login"),
    "credit-exhausted": (403, "account_owner", "The credit is exhausted"),
    "run-budget-exhausted": (403, "account_owner", "The run's budget is exhausted"),
    "key-budget-exhausted": (403, "account_owner", "The key's budget is exhausted"),
    "not-found": (404, "caller", "Not found"),
    "idempotency-key-in-flight": (409, "caller", "The same request is still running"),
    "record-without-content": (409, "caller", "The record has no content"),
    "contents-expired": (410, "caller", "The record has expired"),
    "search-expired": (410, "caller", "The search has expired"),
    "job-expired": (410, "caller", "The job has expired"),
    "body-too-large": (413, "caller", "The body is too large"),
    "unsupported-media-type": (415, "caller", "The media type is not supported"),
    "invalid-field": (422, "caller", "A field is invalid"),
    "destination-refused": (422, "caller", "The destination is refused"),
    "model-work-refused": (422, "caller", "Model work is refused by the request"),
    "cost-exceeds-cap": (422, "caller", "The cost cap is below the smallest call"),
    "version-withdrawn": (422, "caller", "The version is no longer served"),
    "records-incomparable": (422, "caller", "The records cannot be compared"),
    "idempotency-key-reused": (422, "caller", "The idempotency key was reused with another body"),
    "no-datasource-can-run": (422, "caller", "No datasource can run this search"),
    "datasource-unknown": (422, "caller", "The datasource is unknown"),
    "datasource-not-searchable": (422, "caller", "The datasource has no search"),
    "domain-set-unknown": (422, "caller", "The domain set is unknown"),
    "rate-limit-exceeded": (429, "caller", "The rate limit is exceeded"),
    "concurrency-limit-exceeded": (429, "caller", "Too many calls are in flight"),
    "legal-block": (451, "caller", "Withheld under a legal demand"),
    "internal-error": (500, "service", "The service failed"),
    "gateway-error": (502, "service", "A step behind the service failed"),
    "overloaded": (503, "service", "The service is overloaded"),
    "gateway-timeout": (504, "service", "A step behind the service timed out"),
}

RETRYABLE_TYPES = frozenset(
    # The six types a retry can help, as the contract's Problem.retryable names them; false on every other type.
    {
        "idempotency-key-in-flight",
        "rate-limit-exceeded",
        "concurrency-limit-exceeded",
        "overloaded",
        "gateway-error",
        "gateway-timeout",
    }
)

DETAILS: typing.Dict[str, str] = {
    # A problem's detail in the contract's own words, where its answer for the status says what the detail names or
    # one of its examples gives one; every other type's detail is its title as a sentence.
    "unauthorized": (
        "The credential is unknown, expired or revoked: refresh the token, sign in again, or use another key."
    ),
    "page-token-invalid": (
        "The token is unknown, expired, belongs to another record, or the filter changed between pages."
    ),
    "idempotency-key-in-flight": "The first call with this key has not answered yet.",
    "record-without-content": (
        "The record you named failed, was refused or needs a person, so there is no text to read."
    ),
    "destination-refused": "The address is not globally reachable.",
    "invalid-field": EXAMPLES["upload_contents.invalid-field"]["detail"],
    "rate-limit-exceeded": "More requests in the minute than the requests policy allows.",
    "concurrency-limit-exceeded": "More calls at once than the concurrency policy allows.",
    "overloaded": "The request could not start within the published queue bound.",
    "gateway-error": "The model step that is the whole call gave a bad answer.",
    "gateway-timeout": "The model step that is the whole call passed its time bound.",
}

TYPE_MEMBERS: typing.Dict[str, Body] = {
    # The members a type carries beyond the seven every problem has, each where the contract's Problem says it is
    # present, with the contract's own figures where it gives them: a balance of 0.0020 against a call of 0.0050 needing
    # 0.0030; the account owner's page at https://app.getclean.ai; the least cap that runs an upload, the price of one
    # contents; the violations of the upload's own invalid-field example. The contract gives no example of a legal
    # block's three members, so they are plain words of one demand. The scope is the one get_limits needs, the one call
    # these tests refuse for a scope; the id a 404 names is a job's, the one thing these tests find missing.
    "page-token-invalid": {"change": {"field": "page_token"}},
    "invalid-field": {"violations": EXAMPLES["upload_contents.invalid-field"]["violations"]},
    "not-found": {"change": {"field": "job_id"}},
    "record-without-content": {"change": {"operation": "fetch_contents"}},
    "insufficient-scope": {"scopes_required": ["limits:read"]},
    "credit-exhausted": {
        "balance": money("0.0020"),
        "amount_needed": money("0.0030"),
        "funding_url": "https://app.getclean.ai",
    },
    "cost-exceeds-cap": {"minimum_cap": money(price("contents"))},
    "legal-block": {
        "demand": "Withhold the document from every reader.",
        "demanded_by": "A court of record.",
        "applies_to": "The document this upload sent.",
    },
}


def problem(type_name: str, status: typing.Optional[int] = None, **members: typing.Any) -> Body:
    """A problem of this type as the API writes one.

    Its URI, its title and who must act come from the contract's table under Problem.type; the detail is the one
    above; the instance and the request id are those of the answer it comes in, a fresh id unless the test gives one;
    status is set only when given, since a problem nested in a job carries none. Then the members its type carries, and
    the members the case sets; retryable last, true only when the type the body ends with is one of the six a retry can
    help, so a type the case makes up is never retryable.
    """
    _, who_must_act, title = PROBLEM_TABLE[type_name]
    rid = members.pop("request_id", None) or request_id()
    body: Body = {"type": PROBLEM_TYPE_BASE + type_name, "title": title}
    if status is not None:
        body["status"] = status
    body.update(
        detail=DETAILS.get(type_name, f"{title}."),
        instance="https://api.getclean.ai/requests/" + rid,
        request_id=rid,
        who_must_act=who_must_act,
    )
    body.update(copy.deepcopy(TYPE_MEMBERS.get(type_name, {})))
    body.update(members)
    body.setdefault("retryable", body["type"] == PROBLEM_TYPE_BASE + type_name and type_name in RETRYABLE_TYPES)
    return body


# --- the scripted server's answers


class Answer(typing.NamedTuple):
    """One scripted answer: the request it expects, by method and path, and what the server sends back."""

    method: str
    path: str
    status: int
    body: typing.Any = None
    headers: typing.Mapping[str, str] = {}


class Failure(typing.NamedTuple):
    """A request the transport fails before any answer comes, as a refused connection does."""

    method: str
    path: str
    error: Exception


def refusal(
    method: str,
    path: str,
    type_name: str,
    status: int,
    retry_after: typing.Optional[int] = None,
    **members: typing.Any,
) -> Answer:
    """A refusal: the problem of this type at this status and, when the server asks for a wait, the wait in Retry-After
    with the same figure as retry_after_seconds, which the contract makes equal. A 429 and a 503 always ask for one."""
    assert retry_after is not None or status not in (429, 503), (
        "the contract always sends Retry-After on a 429 and a 503"
    )
    assert retry_after is None or retry_after >= 1, "Retry-After is an integer of 1 or more"
    body = problem(type_name, status, **members)
    headers: typing.Dict[str, str] = {}
    if retry_after is not None:
        body["retry_after_seconds"] = retry_after
        headers["Retry-After"] = str(retry_after)
    return Answer(method, path, status, body, headers)


# --- the limits

CONTENTS_CALL_SECONDS = 80.0
"""The contents call_seconds bound the tests' limits carry. The example's own, 110, plus the 10-second margin is 120,
the very timeout the client uses until the limits are read, so a test with it could not tell the two apart."""

JOB_SECONDS = 1200.0
"""The contents job_seconds bound the tests' limits carry. The example's own, 1800, is the 30 minutes the wait uses
until the limits are read, so a test with it could not tell the two apart."""

BOUNDS = {
    # Each family's two call bounds as the tests' limits carry them: the example's own, but for contents call_seconds.
    ("contents", "call_seconds"): CONTENTS_CALL_SECONDS,
    ("contents", "batch_seconds"): float(EXAMPLES["get_limits.limits"]["bounds"]["contents"]["batch_seconds"]["max"]),
    ("search", "call_seconds"): float(EXAMPLES["get_limits.limits"]["bounds"]["search"]["call_seconds"]["max"]),
    ("search", "batch_seconds"): float(EXAMPLES["get_limits.limits"]["bounds"]["search"]["batch_seconds"]["max"]),
}


def limits() -> Body:
    """The limits the tests read: the contract's example, under a request id of its own, with the contents call_seconds
    and job_seconds bounds changed for the reasons above."""
    body = under_request_id(example("get_limits.limits"), request_id())
    body["bounds"]["contents"]["call_seconds"] = {"max": CONTENTS_CALL_SECONDS}
    body["bounds"]["contents"]["job_seconds"] = {"max": JOB_SECONDS}
    return body


def limits_read() -> Answer:
    """get_limits answered with the tests' limits."""
    return Answer("GET", "/v1/limits", 200, limits())


def per_attempt(seconds: float) -> typing.Dict[str, typing.Optional[float]]:
    """A timeout of these seconds on every phase of one attempt, as a request carries it."""
    return httpx.Timeout(seconds).as_dict()


# --- one upload, followed from its answer to its record
#
# The tests that follow an upload follow one: the ten-page minutes.pdf of the upload's 201 example, whose record that
# example carries, parsed as the job of the upload's 202 example. Each state of the job is that job with the members the
# state changes, each set by the contract's rule for it, so that every job agrees with the record it names.

UPLOAD = "/v1/contents:upload"

UPLOADED_RECORD: Body = EXAMPLES["upload_contents.delivered"]["contents"]
"""The record minutes.pdf makes, as the upload's 201 example carries it."""

RECORD_ID: str = UPLOADED_RECORD["id"]
JOB_ID: str = EXAMPLES["upload_contents.job"]["job"]["id"]
UPLOAD_REQUEST_ID: str = EXAMPLES["upload_contents.job"]["request_id"]
"""The upload's own request id, that of its 202 example."""

DOCUMENT = b"%PDF-1.7 minutes of the meeting"
"""The bytes the tests upload, standing for the minutes.pdf of the upload's example."""

NO_PAGES = {"parsed_count": 0, "failed_count": 0, "remaining_count": 0}
"""A job's counts while it is queued or its pages are not counted: zeros (Job.counts)."""

PAGES_DONE_AT_THE_CANCEL = 4
"""How many of minutes.pdf's ten pages were parsed when a cancel came; any number from 1 to 9 would do."""

CORRUPT_DOCUMENT: Body = {
    "kind": "failed",
    "reason": "corrupt_document",
    # In the form of the contract's failed fetch example: what happened, then what may work, as the table under
    # Outcome.reason gives both for corrupt_document.
    "message": "The document could not be opened; the same request will not work.",
}

FAILED_RECORD_MEMBERS = (
    # The members a failed, refused or needs-a-person record carries (Contents), in the order of the contract's failed
    # fetch example; pages only when the page count was read and sections only when the outline was, neither here.
    "id",
    "outcome",
    "notices",
    "fetched_at",
    "truncated",
    "source",
    "execution",
    "cost",
    "retention",
    "run_id",
    "expires_at",
    "request_id",
)


def nothing_billed() -> Body:
    """The cost of a job or a record that billed nothing: actual zero and units {} (Cost.units: "{} when nothing was
    billed"), with the ceiling of the upload's examples, present on every call that can bill."""
    return {"ceiling": money("1.0000"), "actual": money("0.0000"), "units": {}, "replayed": False}


def canceled_cost() -> Body:
    """What the job canceled with pages done bills: 1 contents and a document_pages unit for each page parsed, at the
    prices of the limits example."""
    actual = price("contents") + PAGES_DONE_AT_THE_CANCEL * price("document_pages")
    units = {"contents": 1, "document_pages": PAGES_DONE_AT_THE_CANCEL}
    return {"ceiling": money("1.0000"), "actual": money(actual), "units": units, "replayed": False}


def accepted(job: typing.Optional[Body] = None) -> Answer:
    """The upload's 202: the contract's example, with this job in place of its own when given. Retry-After, always sent
    on a 202, equals the job's retry_after_seconds; Location names the job."""
    body = example("upload_contents.job")
    if job is not None:
        body["job"] = job
    headers = {
        "Retry-After": str(body["job"]["retry_after_seconds"]),
        "Location": f"{BASE_URL}/v1/jobs/{body['job']['id']}",
    }
    return Answer("POST", UPLOAD, 202, body, headers)


def queued() -> Body:
    """The upload's job before its parse starts: the 202 example's job, queued, so with no stage, which is absent while
    queued, counts of zero, which a queued job carries, and nothing billed yet."""
    job = example("upload_contents.job")["job"]
    del job["stage"]
    job.update(state="queued", counts=dict(NO_PAGES), cost=nothing_billed())
    return job


def completed() -> Body:
    """The job completed with minutes.pdf's record: get_job's example with the record's id, outcome and cost, and counts
    of its pages, so the job agrees with the record it names."""
    job = example("get_job.completed")
    pages = UPLOADED_RECORD["pages"]
    failed = len(pages["failed_pages"])
    job.update(
        counts={
            "parsed_count": pages["parsed_count"],
            "failed_count": failed,
            "remaining_count": pages["count"] - pages["parsed_count"] - failed,
        },
        cost=copy.deepcopy(UPLOADED_RECORD["cost"]),
        outcome=copy.deepcopy(UPLOADED_RECORD["outcome"]),
        contents_id=RECORD_ID,
    )
    return job


def failed_with_record() -> Body:
    """The job failed with a record made: get_job's example, failed, the document having not opened, so its record
    carries failed, corrupt_document; no page counted and nothing billed."""
    job = example("get_job.completed")
    job.update(
        state="failed",
        counts=dict(NO_PAGES),
        cost=nothing_billed(),
        outcome=copy.deepcopy(CORRUPT_DOCUMENT),
        contents_id=RECORD_ID,
    )
    return job


def canceled_with_pages() -> Body:
    """The job canceled with pages done: cancel_job's example under this upload's job and record, four of the ten pages
    parsed and billed, the rest left."""
    job = example("cancel_job.canceled")
    job.update(
        id=JOB_ID,
        counts={
            "parsed_count": PAGES_DONE_AT_THE_CANCEL,
            "failed_count": 0,
            "remaining_count": UPLOADED_RECORD["pages"]["count"] - PAGES_DONE_AT_THE_CANCEL,
        },
        cost=canceled_cost(),
        contents_id=RECORD_ID,
    )
    return job


def canceled_without_record() -> Body:
    """The job canceled before any page was done: cancel_job's example under this upload's job, with no record, so no
    outcome and no contents_id, no page counted and nothing billed."""
    job = example("cancel_job.canceled")
    del job["outcome"], job["contents_id"]
    job.update(id=JOB_ID, counts=dict(NO_PAGES), cost=nothing_billed())
    return job


def job_problem(type_name: str, **members: typing.Any) -> Body:
    """A problem as a job carries it: no status, its request id and instance the upload's (Job.problem)."""
    return problem(type_name, request_id=UPLOAD_REQUEST_ID, **members)


def failed_without_record(the_problem: Body) -> Body:
    """The job failed before any record was made: get_job's example, failed, with no record, so no outcome and no
    contents_id, no page counted, nothing billed, and this problem."""
    job = example("get_job.completed")
    del job["outcome"], job["contents_id"]
    job.update(state="failed", counts=dict(NO_PAGES), cost=nothing_billed(), problem=the_problem)
    return job


def polled(job: Body, label: str = "") -> Answer:
    """get_job's answer: this job under the poll's own request id, since a job's request_id is the call it came back in,
    and Retry-After while the job is not finished."""
    body = dict(copy.deepcopy(job), request_id=request_id(label))
    headers = {} if body["finished"] else {"Retry-After": str(body["retry_after_seconds"])}
    return Answer("GET", f"/v1/jobs/{body['id']}", 200, body, headers)


def the_record() -> Body:
    """minutes.pdf's record as get_contents reads it: the upload's 201 example's record under the read's own request
    id."""
    return under_request_id(example("upload_contents.delivered")["contents"], request_id())


def failed_record() -> Body:
    """The record of the document that did not open: minutes.pdf's record with only the members a failed record carries,
    its outcome failed, corrupt_document, nothing billed, and nothing the document says of itself, since it was not
    read."""
    whole = the_record()
    record = {name: whole[name] for name in FAILED_RECORD_MEMBERS}
    record.update(outcome=copy.deepcopy(CORRUPT_DOCUMENT), cost=nothing_billed())
    source = record["source"]
    del source["published_date_precision"], source["published_date_basis"]
    source.update(title=None, published_date=None, modified_date=None, language=None)
    return record


def canceled_record() -> Body:
    """The record of the job canceled with pages done: minutes.pdf's record, partial, canceled, with the pages parsed
    and the cost the canceled job carries."""
    record = the_record()
    record.update(
        outcome={"kind": "partial", "reason": "canceled"},
        pages=dict(record["pages"], parsed_count=PAGES_DONE_AT_THE_CANCEL),
        cost=canceled_cost(),
    )
    return record


def read_of(job: Body, record: Body) -> Answer:
    """get_contents' answer with this record, read under the id the job names."""
    return Answer("GET", f"/v1/contents/{job['contents_id']}", 200, record)


# --- time


class Clock:
    """Time as the client meets it in a test. monotonic() reads a clock that starts at 0; sleep() and async_sleep()
    record each wait the client asks for and move the clock by it instead of waiting; the scripted server moves it by
    the time it holds a poll."""

    def __init__(self) -> None:
        self.now = 0.0
        self.waits: typing.List[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.waits.append(seconds)
        self.now += seconds

    async def async_sleep(self, seconds: float, result: typing.Any = None) -> typing.Any:
        self.sleep(seconds)
        return result

    def advance(self, seconds: float) -> None:
        self.now += seconds


def stand_in_time(monkeypatch: pytest.MonkeyPatch) -> Clock:
    """A Clock in the place of time.monotonic, time.sleep and asyncio.sleep, each replaced at its own module."""
    clock = Clock()
    monkeypatch.setattr(time, "monotonic", clock.monotonic)
    monkeypatch.setattr(time, "sleep", clock.sleep)
    monkeypatch.setattr(asyncio, "sleep", clock.async_sleep)
    return clock


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    """Time stood in for a test, so that no test waits for real, even on a client that waits where it should not."""
    return stand_in_time(monkeypatch)


HIGHEST_DRAW = math.nextafter(1.0, 0.0)
"""The highest value random.random() returns, its range being 0 up to but not including 1."""


def pin_draws(monkeypatch: pytest.MonkeyPatch, end: str) -> None:
    """Pins every random draw a backoff takes at the "lowest" or the "highest" end of the range it asks for:
    random.random and random.uniform at the random module, and the random() the SDK's HTTP runtime binds by name when it
    is imported, which only that name in its own module reaches."""
    lowest = end == "lowest"
    draw = 0.0 if lowest else HIGHEST_DRAW
    monkeypatch.setattr(random, "random", lambda: draw)
    monkeypatch.setattr(random, "uniform", lambda low, high: low if lowest else high)
    monkeypatch.setattr("getclean.core.http_client.random", lambda: draw)


# --- the scripted server

MISDIRECTED = 421
"""The status the scripted server answers a request it did not expect with: 421 Misdirected Request, which no operation
of the API answers, so the client raises it at once and retries nothing."""

RATE_LIMIT = '"requests";r=599;t=60, "concurrency";r=19'
RATE_LIMIT_POLICY = '"requests";q=600;w=60, "concurrency";q=20;qu="concurrent-requests"'
"""The quota headers every answer but a 401 carries, in the contract's form, on the rates of the limits example: 600
requests a minute, 20 calls in flight."""

REJECTED_CREDENTIAL = (
    'Bearer realm="getclean", error="invalid_token", '
    'resource_metadata="https://api.getclean.ai/.well-known/oauth-protected-resource"'
)
"""The WWW-Authenticate value of a 401 to a credential sent and rejected, as the contract gives it."""


def _a_held_poll(request: httpx.Request, answer: Answer) -> bool:
    """Whether the server holds this request for its whole wait: a poll of a job that is not finished (get_job: the
    answer comes at the final state or when wait_seconds ends)."""
    return (
        request.method == "GET"
        and request.url.path.startswith("/v1/jobs/")
        and "wait_seconds" in request.url.params
        and isinstance(answer.body, dict)
        and answer.body.get("finished") is False
    )


def _response(request: httpx.Request, answer: Answer) -> httpx.Response:
    """The answer as the server sends it, with the headers the contract requires on every answer: Request-Id, the
    body's request_id or a fresh one where no body is sent; the quota headers on every status but 401;
    WWW-Authenticate on a 401; then the answer's own headers."""
    body_id = answer.body.get("request_id") if isinstance(answer.body, dict) else None
    headers: typing.Dict[str, str] = {"Request-Id": body_id or request_id()}
    if answer.status == 401:
        headers["WWW-Authenticate"] = REJECTED_CREDENTIAL
    else:
        headers.update({"RateLimit": RATE_LIMIT, "RateLimit-Policy": RATE_LIMIT_POLICY})
    headers.update(answer.headers)
    if answer.body is None:
        return httpx.Response(answer.status, headers=headers, request=request)
    content = answer.body if isinstance(answer.body, bytes) else json.dumps(answer.body).encode()
    headers["Content-Type"] = "application/problem+json" if answer.status >= 400 else "application/json"
    return httpx.Response(answer.status, content=content, headers=headers, request=request)


def default_client(
    client_class: type,
    monkeypatch: pytest.MonkeyPatch,
    handler: typing.Callable[..., typing.Any],
    **options: typing.Any,
) -> typing.Any:
    """A client of this class built as a caller builds one, with no HTTP client and no timeout of the caller's own,
    whose requests the handler answers: the transport the client makes for itself is the handler's, and the optional
    aiohttp client, which the async client takes when it is installed, is kept out."""
    options.setdefault("api_key", "key")
    options.setdefault("base_url", BASE_URL)
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(httpx, "HTTPTransport", lambda *args, **kwargs: transport)
    monkeypatch.setattr(httpx, "AsyncHTTPTransport", lambda *args, **kwargs: transport)
    monkeypatch.setitem(sys.modules, "httpx_aiohttp", None)
    return client_class(**options)


class Script:
    """A server that answers in the order the test wrote and keeps every request. A request it did not expect, or one
    after the last answer, is recorded in `unexpected` and answered 421; the step it expected stays for the next
    request. With a clock, a held poll moves the clock by the wait the poll asked for."""

    def __init__(
        self,
        steps: typing.Sequence[typing.Union[Answer, Failure]],
        clock: typing.Optional[Clock] = None,
    ) -> None:
        self.steps: typing.List[typing.Union[Answer, Failure]] = list(steps)
        self.requests: typing.List[httpx.Request] = []
        self.unexpected: typing.List[str] = []
        self.clock = clock

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        step = self.steps[0] if self.steps else None
        if step is None or (request.method, request.url.path) != (step.method, step.path):
            sent = f"{request.method} {request.url.path}"
            self.unexpected.append(sent)
            expected = f"{step.method} {step.path}" if step is not None else "no further request"
            return httpx.Response(MISDIRECTED, json={"unexpected": sent, "expected": expected}, request=request)
        self.steps.pop(0)
        if isinstance(step, Failure):
            raise step.error
        if self.clock is not None and _a_held_poll(request, step):
            self.clock.advance(float(request.url.params["wait_seconds"]))
        return _response(request, step)

    def sent(self, method: str, path: str) -> typing.List[httpx.Request]:
        """The requests sent to this method and path, in order."""
        return [request for request in self.requests if (request.method, request.url.path) == (method, path)]

    @property
    def unanswered(self) -> typing.List[typing.Union[Answer, Failure]]:
        """The scripted answers no request has taken."""
        return list(self.steps)

    def client(self, **options: typing.Any) -> GetClean:
        """A GetClean handed the caller's own HTTP client, whose requests this script answers: the key "key" and the
        test host unless the test gives others."""
        options.setdefault("api_key", "key")
        options.setdefault("base_url", BASE_URL)
        transport = httpx.MockTransport(self)
        return GetClean(httpx_client=httpx.Client(transport=transport, timeout=CLIENT_TIMEOUT), **options)

    def async_client(self, **options: typing.Any) -> AsyncGetClean:
        """An AsyncGetClean handed the caller's own HTTP client, as client() builds a GetClean."""
        options.setdefault("api_key", "key")
        options.setdefault("base_url", BASE_URL)
        transport = httpx.MockTransport(self)
        return AsyncGetClean(httpx_client=httpx.AsyncClient(transport=transport, timeout=CLIENT_TIMEOUT), **options)

    def base_client_for(self, client_class: type) -> typing.Any:
        """The base client the client of this class is built on, BaseGetClean or AsyncBaseGetClean, handed the caller's
        own HTTP client on this script: what a call sends with none of the client's additions."""
        transport = httpx.MockTransport(self)
        options: typing.Dict[str, typing.Any] = {"api_key": "key", "base_url": BASE_URL}
        if client_class is GetClean:
            return BaseGetClean(httpx_client=httpx.Client(transport=transport, timeout=CLIENT_TIMEOUT), **options)
        return AsyncBaseGetClean(httpx_client=httpx.AsyncClient(transport=transport, timeout=CLIENT_TIMEOUT), **options)

    def client_for(self, client_class: type, **options: typing.Any) -> typing.Any:
        """The client of this class on this script, handed the caller's own HTTP client."""
        return self.client(**options) if client_class is GetClean else self.async_client(**options)

    def default_client(self, client_class: type, monkeypatch: pytest.MonkeyPatch, **options: typing.Any) -> typing.Any:
        """The client of this class on this script, built as a caller builds one with no HTTP client of its own."""
        return default_client(client_class, monkeypatch, self, **options)


# --- the calls the tests make


class Call(typing.NamedTuple):
    """A call as a test makes it: the method and the arguments of the API's request example, where it goes, and the name
    of the API's example of its answer. For a call that may bill, family and bound name the bound of the limits that
    times each of its attempts."""

    method: str
    args: typing.Tuple[typing.Any, ...]
    kwargs: Body
    http_method: str
    path: str
    status: int
    example: str
    family: str = ""
    bound: str = ""

    def on(self, client: typing.Any, **extra: typing.Any) -> typing.Any:
        """The call made on this client with any extra arguments; awaitable on the async client."""
        return getattr(client, self.method)(*self.args, **{**self.kwargs, **extra})

    def answered(self) -> Answer:
        """Its success answer: the API's example of it under a request id of its own, with Location naming what a 201
        made; a 204 carries no body."""
        if not self.example:
            return Answer(self.http_method, self.path, self.status)
        body = under_request_id(example(self.example), request_id())
        headers: typing.Dict[str, str] = {}
        if self.status == 201:
            made = body.get("contents", body)
            kind = "search" if made["id"].startswith("srch_") else "contents"
            headers["Location"] = f"{BASE_URL}/v1/{kind}/{made['id']}"
        return Answer(self.http_method, self.path, self.status, body, headers)

    def refused(
        self, type_name: str, status: int, retry_after: typing.Optional[int] = None, **members: typing.Any
    ) -> Answer:
        """A refusal of this call: the problem of this type at this status, with the server's wait when given."""
        return refusal(self.http_method, self.path, type_name, status, retry_after, **members)


CONTENTS_ID: str = EXAMPLES["get_section.fits"]["contents_id"]
"""The record of the API's examples of get_section, list_blocks, list_links, highlight_contents, fill_schema and
summarize_contents."""

BILLED_CALLS = [
    # The eight calls that may bill, each with arguments from the API's request example, the name of its answer example,
    # and the bound that times it: batch_seconds for the two batches, call_seconds for the other six.
    Call(
        "fetch_contents",
        (),
        {"url": "https://example.com/q3"},
        "POST",
        "/v1/contents",
        201,
        "fetch_contents.delivered",
        "contents",
        "call_seconds",
    ),
    Call(
        "fetch_contents_batch",
        (),
        {"items": [ContentsBatchItem(url="https://a.example/report", label="a")]},
        "POST",
        "/v1/contents:batch",
        200,
        "fetch_contents_batch.mixed",
        "contents",
        "batch_seconds",
    ),
    Call(
        "highlight_contents",
        (CONTENTS_ID,),
        {"highlights": ["Revenue rose 12%", "dividend policy"]},
        "POST",
        f"/v1/contents/{CONTENTS_ID}:highlight",
        200,
        "highlight_contents.found",
        "contents",
        "call_seconds",
    ),
    Call(
        "fill_schema",
        (CONTENTS_ID,),
        {
            "json_schema": {
                "type": "object",
                "properties": {"revenue_growth": {"type": "string"}, "dividend": {"type": "string"}},
            }
        },
        "POST",
        f"/v1/contents/{CONTENTS_ID}:fill",
        200,
        "fill_schema.filled",
        "contents",
        "call_seconds",
    ),
    Call(
        "summarize_contents",
        (CONTENTS_ID,),
        {},
        "POST",
        f"/v1/contents/{CONTENTS_ID}:summarize",
        200,
        "summarize_contents.summary",
        "contents",
        "call_seconds",
    ),
    Call(
        "search",
        (),
        {"query": "EU AI Act article 50 marking obligations"},
        "POST",
        "/v1/search",
        201,
        "search.delivered",
        "search",
        "call_seconds",
    ),
    Call(
        "search_batch",
        (),
        {"items": [SearchBatchItem(label="a", query="EU AI Act article 50 marking obligations")]},
        "POST",
        "/v1/search:batch",
        200,
        "search_batch.mixed",
        "search",
        "batch_seconds",
    ),
    Call(
        "upload_contents",
        (),
        {"document": DOCUMENT},
        "POST",
        UPLOAD,
        201,
        "upload_contents.delivered",
        "contents",
        "call_seconds",
    ),
]

FETCH, BATCH, HIGHLIGHT, FILL, SUMMARIZE, SEARCH, SEARCH_BATCH, UPLOAD_CALL = BILLED_CALLS


def _read(method: str, args: typing.Tuple[typing.Any, ...], path: str, name: str) -> Call:
    return Call(method, args, {}, "GET", path, 200, name)


FREE_READS = [
    # The reads and the delete, which bill nothing: every GET and the DELETE, with the ids and the answers of the API's
    # examples; a delete answers 204 with no body.
    _read("list_contents", (), "/v1/contents", "list_contents.first-page"),
    _read(
        "get_contents",
        (EXAMPLES["get_contents.delivered"]["id"],),
        f"/v1/contents/{EXAMPLES['get_contents.delivered']['id']}",
        "get_contents.delivered",
    ),
    Call("delete_contents", (CONTENTS_ID,), {}, "DELETE", f"/v1/contents/{CONTENTS_ID}", 204, ""),
    _read(
        "get_section",
        (CONTENTS_ID, EXAMPLES["get_section.fits"]["section"]["id"]),
        f"/v1/contents/{CONTENTS_ID}/sections/{EXAMPLES['get_section.fits']['section']['id']}",
        "get_section.fits",
    ),
    _read("list_blocks", (CONTENTS_ID,), f"/v1/contents/{CONTENTS_ID}/blocks", "list_blocks.first-page"),
    _read("list_links", (CONTENTS_ID,), f"/v1/contents/{CONTENTS_ID}/links", "list_links.first-page"),
    _read("list_jobs", (), "/v1/jobs", "list_jobs.first-page"),
    _read(
        "get_job",
        (EXAMPLES["get_job.completed"]["id"],),
        f"/v1/jobs/{EXAMPLES['get_job.completed']['id']}",
        "get_job.completed",
    ),
    _read("get_limits", (), "/v1/limits", "get_limits.limits"),
    _read(
        "get_search",
        (EXAMPLES["get_search.delivered"]["id"],),
        f"/v1/search/{EXAMPLES['get_search.delivered']['id']}",
        "get_search.delivered",
    ),
    _read("list_datasources", (), "/v1/datasources", "list_datasources.first-page"),
    _read(
        "get_datasource",
        (EXAMPLES["get_datasource.entry"]["id"],),
        f"/v1/datasources/{EXAMPLES['get_datasource.entry']['id']}",
        "get_datasource.entry",
    ),
]

FREE_POSTS = [
    # The two POSTs that bill nothing and take no key, with the ids and the answers of the API's examples.
    Call(
        "cancel_job",
        (EXAMPLES["cancel_job.canceled"]["id"],),
        {},
        "POST",
        f"/v1/jobs/{EXAMPLES['cancel_job.canceled']['id']}:cancel",
        200,
        "cancel_job.canceled",
    ),
    Call(
        "compare_contents",
        (EXAMPLES["compare_contents.changed"]["contents_id"],),
        {"baseline_contents_id": EXAMPLES["compare_contents.changed"]["baseline_contents_id"]},
        "POST",
        f"/v1/contents/{EXAMPLES['compare_contents.changed']['contents_id']}:compare",
        200,
        "compare_contents.changed",
    ),
]


def ids(calls: typing.Sequence[Call]) -> typing.List[str]:
    """The test ids of a list of calls: their method names."""
    return [call.method for call in calls]


# --- the clients' two forms, read as one


async def settle(result: typing.Union[T, typing.Awaitable[T]]) -> T:
    """What a call returns: awaited when the client is AsyncGetClean, as it is when the client is GetClean."""
    if inspect.isawaitable(result):
        return typing.cast(T, await result)
    return typing.cast(T, result)


async def items_of(pager: typing.Any) -> typing.List[typing.Any]:
    """Every item a pager yields, iterated as a caller iterates it: async for on an AsyncPager, for on a SyncPager."""
    if isinstance(pager, AsyncPager):
        return [item async for item in pager]
    return list(pager)


async def pages_of(pager: typing.Any) -> typing.List[typing.Any]:
    """Every page a pager yields through iter_pages, in either form."""
    if isinstance(pager, AsyncPager):
        return [page async for page in pager.iter_pages()]
    return list(pager.iter_pages())


async def drain(iterator: typing.Any, into: typing.List[typing.Any]) -> None:
    """Appends each element of an iterator or an async iterator to `into` as it comes, so the elements yielded before an
    error stay readable after it."""
    if hasattr(iterator, "__aiter__"):
        async for element in iterator:
            into.append(element)
    else:
        for element in iterator:
            into.append(element)


# --- a multipart body as the server reads it


class Part(typing.NamedTuple):
    """One part of a multipart/form-data body."""

    name: str
    filename: typing.Optional[str]
    content_type: typing.Optional[str]
    content: bytes


def form_parts(request: httpx.Request) -> typing.List[Part]:
    """The parts of a multipart/form-data request, read from the bytes it sent (RFC 7578)."""
    media_type = email.message.Message()
    media_type["content-type"] = request.headers["Content-Type"]
    boundary = media_type.get_param("boundary")
    assert media_type.get_content_type() == "multipart/form-data" and isinstance(boundary, str), (
        f"an upload is sent as multipart/form-data: {request.headers['Content-Type']}"
    )
    parts = []
    for chunk in request.content.split(b"--" + boundary.encode())[1:-1]:
        head, _, content = chunk.removeprefix(b"\r\n").partition(b"\r\n\r\n")
        fields = email.message.Message()
        for line in head.decode().split("\r\n"):
            key, _, value = line.partition(": ")
            fields[key] = value
        name = fields.get_param("name", header="content-disposition")
        filename = fields.get_param("filename", header="content-disposition")
        assert isinstance(name, str) and (filename is None or isinstance(filename, str)), (
            f"each part names itself in Content-Disposition: {head!r}"
        )
        parts.append(Part(name, filename, fields.get("content-type"), content.removesuffix(b"\r\n")))
    return parts


def the_document(request: httpx.Request) -> Part:
    """The one part named document of an upload."""
    parts = [part for part in form_parts(request) if part.name == "document"]
    assert len(parts) == 1, f"an upload sends one document part: {[part.name for part in form_parts(request)]}"
    return parts[0]
