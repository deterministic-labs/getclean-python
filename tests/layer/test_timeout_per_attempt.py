"""The timeout of each attempt of a call that may bill, and the reading of the limits it comes from: the operation's own
bound plus ten seconds once the limits are read, 120 seconds until then, and the caller's own wherever the call or the
client sets one; a limits read that never fails the call, read again after a transient failure and never after a 401 or
a 403, carrying the call's headers alone."""

import asyncio
import typing

import httpx
import pytest
from ._support import (
    BATCH,
    BILLED_CALLS,
    BOUNDS,
    CLIENT_TIMEOUT,
    CLIENTS,
    FETCH,
    SEARCH,
    Answer,
    Body,
    Call,
    Failure,
    Script,
    clock,
    default_client,
    ids,
    limits,
    limits_read,
    per_attempt,
    refusal,
    request_id,
    settle,
)

from getclean import AsyncGetClean
from getclean.errors import UnauthorizedError

# Every test of this file runs with time stood in, so that none waits for real, even on a client that waits
# where it should not.
pytestmark = pytest.mark.usefixtures(clock.__name__)

UNTIL_READ_SECONDS = 120
"""The timeout of each attempt until the limits are read."""

MARGIN_SECONDS = 10
"""What the timeout of each attempt adds to the operation's bound, for the network."""

TRACEPARENT = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
"""A caller's header, the example of the W3C Trace Context recommendation."""

YIELD_TO_THE_LOOP = asyncio.sleep
"""The real asyncio.sleep, kept before time is stood in for each test: sleep(0) yields to the event loop once and waits
for nothing."""


def timeout_of(call: Call) -> typing.Dict[str, typing.Optional[float]]:
    """The timeout each attempt of a call that may bill carries once the limits are read: its own bound plus ten."""
    return per_attempt(BOUNDS[(call.family, call.bound)] + MARGIN_SECONDS)


def limits_without(family: str, bound: str, how: str) -> Body:
    """The tests' limits with this bound left out, or carried with no max, every member of a bound being optional."""
    body = limits()
    if how == "absent":
        del body["bounds"][family][bound]
    else:
        body["bounds"][family][bound] = {}
    return body


def unparsable_limits() -> Body:
    """An answer to get_limits that does not parse: the tests' limits with bounds, a required member, left out."""
    body = limits()
    del body["bounds"]
    return body


@CLIENTS
async def test_the_limits_are_read_once_before_the_first_call_that_may_bill(client_class: type) -> None:
    """The limits are read before the first call that may bill, and once only: three calls, one read."""
    script = Script([limits_read(), FETCH.answered(), SEARCH.answered(), FETCH.answered()])
    client = script.client_for(client_class)

    await settle(FETCH.on(client))
    await settle(SEARCH.on(client))
    await settle(FETCH.on(client))

    assert [(r.method, r.url.path) for r in script.requests] == [
        ("GET", "/v1/limits"),
        ("POST", "/v1/contents"),
        ("POST", "/v1/search"),
        ("POST", "/v1/contents"),
    ], "the limits are read first, and once"
    assert script.unexpected == [], f"only the requests the calls call for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("call", BILLED_CALLS, ids=ids(BILLED_CALLS))
async def test_a_billed_call_goes_out_under_its_operations_own_bound_plus_ten_seconds(
    monkeypatch: pytest.MonkeyPatch, client_class: type, call: Call
) -> None:
    """On a client built with no timeout and no HTTP client of the caller's, each call that may bill goes out under its
    operation's own bound plus ten seconds: batch_seconds for the two batches, call_seconds for the other six."""
    script = Script([limits_read(), call.answered()])

    await settle(call.on(script.default_client(client_class, monkeypatch)))

    (sent,) = script.sent(call.http_method, call.path)
    assert sent.extensions["timeout"] == timeout_of(call), f"the {call.bound} bound plus ten seconds"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
async def test_until_the_limits_are_read_a_billed_call_goes_out_under_120_seconds(
    monkeypatch: pytest.MonkeyPatch, client_class: type
) -> None:
    """A call that may bill whose limits read failed goes out under 120 seconds."""
    script = Script([refusal("GET", "/v1/limits", "internal-error", 500), FETCH.answered()])

    await settle(FETCH.on(script.default_client(client_class, monkeypatch)))

    (sent,) = script.sent("POST", "/v1/contents")
    assert sent.extensions["timeout"] == per_attempt(UNTIL_READ_SECONDS), "120 seconds until the limits are read"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("option", ["timeout", "timeout_in_seconds"])
async def test_a_timeout_the_call_gives_stands(
    monkeypatch: pytest.MonkeyPatch, client_class: type, option: str
) -> None:
    """A timeout the call's request options give, under either name, is the one the call goes out under."""
    callers_seconds = 33  # a figure no rule of the client gives: neither 120 nor a bound plus ten
    script = Script([limits_read(), FETCH.answered()])

    await settle(FETCH.on(script.default_client(client_class, monkeypatch), request_options={option: callers_seconds}))

    (sent,) = script.sent("POST", "/v1/contents")
    assert sent.extensions["timeout"] == per_attempt(callers_seconds), "the call's own timeout stands"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
async def test_a_timeout_the_client_was_built_with_stands(monkeypatch: pytest.MonkeyPatch, client_class: type) -> None:
    """A timeout given when the client was built is the one every call that may bill goes out under."""
    clients_seconds = 33  # a figure no rule of the client gives
    script = Script([limits_read(), FETCH.answered(), BATCH.answered()])
    client = script.default_client(client_class, monkeypatch, timeout=clients_seconds)

    await settle(FETCH.on(client))
    await settle(BATCH.on(client))

    sent = [script.sent("POST", "/v1/contents")[0], script.sent("POST", "/v1/contents:batch")[0]]
    assert [r.extensions["timeout"] for r in sent] == [per_attempt(clients_seconds)] * 2, (
        "the timeout the client was built with stands"
    )
    assert script.unexpected == [], f"only the requests the calls call for: {script.unexpected}"


@CLIENTS
async def test_the_timeout_of_the_callers_own_http_client_stands(client_class: type) -> None:
    """A client handed the caller's own HTTP client keeps that client's timeout on every call that may bill."""
    script = Script([limits_read(), FETCH.answered(), BATCH.answered()])
    client = script.client_for(client_class)

    await settle(FETCH.on(client))
    await settle(BATCH.on(client))

    sent = [script.sent("POST", "/v1/contents")[0], script.sent("POST", "/v1/contents:batch")[0]]
    assert [r.extensions["timeout"] for r in sent] == [CLIENT_TIMEOUT.as_dict()] * 2, (
        "the timeout of the caller's own HTTP client stands"
    )
    assert script.unexpected == [], f"only the requests the calls call for: {script.unexpected}"


LIMITS_READ_FAILURES: typing.Dict[str, typing.List[typing.Union[Answer, Failure]]] = {
    # A limits read that ends without limits, each as the client meets it. A 429, a 503 and a refused connection are
    # retried, five attempts in all, each 429 and 503 asking a wait of 1 second.
    "401": [refusal("GET", "/v1/limits", "unauthorized", 401)],
    "403": [refusal("GET", "/v1/limits", "insufficient-scope", 403)],
    "429 on every attempt": [refusal("GET", "/v1/limits", "rate-limit-exceeded", 429, retry_after=1) for _ in range(5)],
    "500": [refusal("GET", "/v1/limits", "internal-error", 500)],
    "503 on every attempt": [refusal("GET", "/v1/limits", "overloaded", 503, retry_after=1) for _ in range(5)],
    "no answer": [Failure("GET", "/v1/limits", httpx.ConnectError("connection refused")) for _ in range(5)],
    "an answer that does not parse": [Answer("GET", "/v1/limits", 200, unparsable_limits())],
}
PASSING_FAILURES = {name: LIMITS_READ_FAILURES[name] for name in LIMITS_READ_FAILURES if name not in ("401", "403")}


@CLIENTS
@pytest.mark.parametrize("failure", LIMITS_READ_FAILURES.values(), ids=LIMITS_READ_FAILURES.keys())
async def test_a_failed_limits_read_leaves_the_defaults_and_never_fails_the_call(
    monkeypatch: pytest.MonkeyPatch, client_class: type, failure: typing.List[typing.Union[Answer, Failure]]
) -> None:
    """A limits read that fails for any reason, refused, failing on the service's side, unanswered or not parsing,
    leaves 120 seconds; the call that may bill goes out and returns its own answer, and nothing else is raised."""
    answer = FETCH.answered()
    script = Script([*failure, answer])

    contents = await settle(FETCH.on(script.default_client(client_class, monkeypatch)))

    assert contents.request_id == answer.body["request_id"], "the call returns its own answer"
    (sent,) = script.sent("POST", "/v1/contents")
    assert sent.extensions["timeout"] == per_attempt(UNTIL_READ_SECONDS), "a failed read leaves 120 seconds"
    assert script.unanswered == [], "the read went through every attempt it is given"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
async def test_a_billed_call_raises_its_own_refusal_not_the_limits_reads(client_class: type) -> None:
    """When the limits read and the call are both refused, the error raised is the call's own answer."""
    script = Script(
        [
            refusal("GET", "/v1/limits", "unauthorized", 401, request_id=request_id("LimitsRead")),
            FETCH.refused("unauthorized", 401, request_id=request_id("BilledCall")),
        ]
    )

    with pytest.raises(UnauthorizedError) as raised:
        await settle(FETCH.on(script.client_for(client_class)))

    assert raised.value.body.request_id == request_id("BilledCall"), "the error is the billed call's own refusal"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("refused", ["401", "403"])
async def test_after_a_401_or_a_403_the_limits_are_not_read_again(client_class: type, refused: str) -> None:
    """A limits read refused 401 or 403 is not repeated for the client's life: the later calls that may bill go out with
    no read before them."""
    script = Script([*LIMITS_READ_FAILURES[refused], FETCH.answered(), FETCH.answered(), SEARCH.answered()])
    client = script.client_for(client_class)

    for call in (FETCH, FETCH, SEARCH):
        await settle(call.on(client))

    assert [(r.method, r.url.path) for r in script.requests] == [
        ("GET", "/v1/limits"),
        ("POST", "/v1/contents"),
        ("POST", "/v1/contents"),
        ("POST", "/v1/search"),
    ], "a read refused 401 or 403 is never repeated"
    assert script.unexpected == [], f"only the requests the calls call for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("failure", PASSING_FAILURES.values(), ids=PASSING_FAILURES.keys())
async def test_after_a_passing_failure_the_limits_are_read_again_before_the_next_billed_call(
    monkeypatch: pytest.MonkeyPatch, client_class: type, failure: typing.List[typing.Union[Answer, Failure]]
) -> None:
    """After a limits read that ended in a 429, a 5xx, no answer or an answer that does not parse, the next call that
    may bill reads them again, and once a read succeeds the calls go out under the bound it gave and nothing is read
    again."""
    script = Script([*failure, FETCH.answered(), limits_read(), FETCH.answered(), FETCH.answered()])
    client = script.default_client(client_class, monkeypatch)

    for _ in range(3):
        await settle(FETCH.on(client))

    after_the_failure = [(r.method, r.url.path) for r in script.requests][len(failure) :]
    assert after_the_failure == [
        ("POST", "/v1/contents"),
        ("GET", "/v1/limits"),
        ("POST", "/v1/contents"),
        ("POST", "/v1/contents"),
    ], "read again before the next call after the failed read, then never again"
    timeouts = [r.extensions["timeout"] for r in script.sent("POST", "/v1/contents")]
    assert timeouts == [per_attempt(UNTIL_READ_SECONDS)] + [timeout_of(FETCH)] * 2, (
        "120 seconds before the limits are read, the bound plus ten after"
    )
    assert script.unexpected == [], f"only the requests the calls call for: {script.unexpected}"


@CLIENTS
async def test_the_limits_read_carries_the_calls_headers_and_none_of_its_other_options(client_class: type) -> None:
    """The limits read before a call that may bill carries that call's headers and none of its other request options:
    no query parameter and no body member of the call's, the client's own timeout, not the call's, and its own count of
    attempts, not the call's max_retries: refused 503 four times, the read is tried again until its fifth attempt,
    while the call itself, given max_retries 0, makes one."""
    answer = FETCH.answered()
    script = Script(
        [*[refusal("GET", "/v1/limits", "overloaded", 503, retry_after=1) for _ in range(4)], limits_read(), answer]
    )
    options = {
        "additional_headers": {"traceparent": TRACEPARENT},
        "additional_query_parameters": {"trace": "on"},
        "additional_body_parameters": {"note": "for the call alone"},
        "timeout": 33,
        "max_retries": 0,
    }

    await settle(FETCH.on(script.client_for(client_class), request_options=options))

    reads = script.sent("GET", "/v1/limits")
    (call,) = script.sent("POST", "/v1/contents")
    assert len(reads) == 5, f"the read keeps its own count of attempts, not the call's max_retries: {len(reads)}"
    assert all(read.headers.get("traceparent") == TRACEPARENT for read in reads), "the call's headers on the read"
    assert all("trace" not in read.url.params for read in reads), "none of the call's query parameters on the read"
    assert all(read.content == b"" for read in reads), "none of the call's body members on the read"
    assert all(read.extensions["timeout"] == CLIENT_TIMEOUT.as_dict() for read in reads), (
        "the read keeps the client's own timeout, not the call's"
    )
    assert call.url.params.get("trace") == "on" and b'"note"' in call.content, "the call itself carried its options"
    assert call.extensions["timeout"] == per_attempt(33), "the call itself went out under its own timeout"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


LACKING = [
    # (the call, the family and the bound the limits lack, how they lack it)
    (FETCH, "contents", "call_seconds", "absent"),
    (FETCH, "contents", "call_seconds", "without a max"),
    (BATCH, "contents", "batch_seconds", "absent"),
]


@CLIENTS
@pytest.mark.parametrize(
    "call, family, bound, how",
    LACKING,
    ids=["call_seconds absent", "call_seconds without a max", "batch_seconds absent"],
)
async def test_a_call_whose_bound_the_limits_lack_goes_out_under_120_seconds(
    monkeypatch: pytest.MonkeyPatch, client_class: type, call: Call, family: str, bound: str, how: str
) -> None:
    """Limits that lack a call's own bound, or carry it with no max, leave that call under 120 seconds with no error,
    while a call of the other family takes its own bound."""
    script = Script(
        [Answer("GET", "/v1/limits", 200, limits_without(family, bound, how)), call.answered(), SEARCH.answered()]
    )
    client = script.default_client(client_class, monkeypatch)

    await settle(call.on(client))
    await settle(SEARCH.on(client))

    (lacking,) = script.sent(call.http_method, call.path)
    (search,) = script.sent("POST", "/v1/search")
    assert lacking.extensions["timeout"] == per_attempt(UNTIL_READ_SECONDS), f"120 seconds without its {bound} bound"
    assert search.extensions["timeout"] == timeout_of(SEARCH), "the other family's own bound plus ten"
    assert script.unexpected == [], f"only the requests the calls call for: {script.unexpected}"


async def test_two_first_calls_at_once_each_go_out_and_read_the_limits_at_most_twice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two calls that may bill, started together before the limits are read, each go out under the bound they read; the
    limits are read at most twice, once by each, and never again after."""
    requests: typing.List[httpx.Request] = []
    answer = FETCH.answered()

    async def server(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/v1/limits":
            await YIELD_TO_THE_LOOP(0)  # the read yields, so the second call starts while the first one's read is open
            return httpx.Response(200, json=limits(), request=request)
        return httpx.Response(201, json=answer.body, headers=dict(answer.headers), request=request)

    client = default_client(AsyncGetClean, monkeypatch, server)

    await asyncio.gather(FETCH.on(client), FETCH.on(client))
    reads_before_the_third = [r for r in requests if r.url.path == "/v1/limits"]
    await FETCH.on(client)

    calls = [r for r in requests if r.url.path == "/v1/contents"]
    assert len(calls) == 3 and len({r.headers["Idempotency-Key"] for r in calls}) == 3, "each call went out once"
    assert 1 <= len(reads_before_the_third) <= 2, f"the limits read at most twice: {len(reads_before_the_third)}"
    assert len([r for r in requests if r.url.path == "/v1/limits"]) == len(reads_before_the_third), (
        "the limits are never read again once read"
    )
    assert all(r.extensions["timeout"] == timeout_of(FETCH) for r in calls), "each call under the bound it read"


@CLIENTS
async def test_the_retry_of_a_503_keeps_the_timeout_per_attempt(
    monkeypatch: pytest.MonkeyPatch, client_class: type
) -> None:
    """A 503 retried inside a call that may bill: each attempt goes out under the same timeout, the operation's bound
    plus ten seconds, since the timeout bounds each attempt and not the call."""
    script = Script([limits_read(), FETCH.refused("overloaded", 503, retry_after=1), FETCH.answered()])

    await settle(FETCH.on(script.default_client(client_class, monkeypatch)))

    attempts = script.sent("POST", "/v1/contents")
    assert len(attempts) == 2, "the 503 is retried once"
    assert all(r.extensions["timeout"] == timeout_of(FETCH) for r in attempts), "each attempt under the bound plus ten"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"
