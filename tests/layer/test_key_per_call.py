"""One idempotency key per call that may bill: a fresh one when the caller gives none, the caller's own when given, the
same on every attempt of the call, and on every error the call raises; and nothing of the client's own on the calls
that never bill."""

import typing
import uuid

import httpx
import pytest
from ._support import (
    BILLED_CALLS,
    CLIENT_TIMEOUT,
    CLIENTS,
    FETCH,
    FREE_POSTS,
    FREE_READS,
    Answer,
    Call,
    Clock,
    Failure,
    Script,
    clock,
    ids,
    limits_read,
    settle,
)

from getclean.errors import NotFoundError, ServiceUnavailableError, UnauthorizedError

# Every test of this file runs with time stood in, so that none waits for real, even on a client that waits
# where it should not.
pytestmark = pytest.mark.usefixtures(clock.__name__)

CALLERS_KEY = '"order-7:retry"'
"""A key a caller gives, visible ASCII used exactly as sent: the contract keeps even a quoted value's quotes as part of
the key."""


def is_uuid4(key: object) -> bool:
    """Whether the key is a UUID version 4 in its canonical text form, the form of a key the SDK makes."""
    if not isinstance(key, str):
        return False
    try:
        parsed = uuid.UUID(key)
    except ValueError:
        return False
    return parsed.version == 4 and str(parsed) == key


def keys_sent(script: Script, call: Call) -> typing.List[typing.Optional[str]]:
    return [request.headers.get("Idempotency-Key") for request in script.sent(call.http_method, call.path)]


@CLIENTS
@pytest.mark.parametrize("call", BILLED_CALLS, ids=ids(BILLED_CALLS))
async def test_a_billed_call_without_a_key_sends_a_fresh_uuid4_key(client_class: type, call: Call) -> None:
    """A call that may bill, given no key, sends a UUID v4 key, a new one for each call: two calls compared."""
    script = Script([limits_read(), call.answered(), call.answered()])
    client = script.client_for(client_class)

    await settle(call.on(client))
    await settle(call.on(client))

    keys = keys_sent(script, call)
    assert len(keys) == 2 and all(is_uuid4(key) for key in keys), f"a UUID v4 key on each call: {keys}"
    assert keys[0] != keys[1], f"a fresh key for each call: {keys}"
    assert script.unexpected == [], f"only the requests the calls call for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("call", BILLED_CALLS, ids=ids(BILLED_CALLS))
async def test_the_callers_key_goes_unchanged_on_every_attempt(client_class: type, call: Call) -> None:
    """A key the caller gives goes out as given on every attempt of the call: the retry after a 503 and the retry after
    an in-flight 409 alike."""
    script = Script(
        [
            limits_read(),
            call.refused("overloaded", 503, retry_after=1),
            call.refused("idempotency-key-in-flight", 409, retry_after=1),
            call.answered(),
        ]
    )

    await settle(call.on(script.client_for(client_class), idempotency_key=CALLERS_KEY))

    sent = keys_sent(script, call)
    assert sent == [CALLERS_KEY] * 3, f"the caller's key, unchanged, on all three attempts: {sent}"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("call", BILLED_CALLS, ids=ids(BILLED_CALLS))
async def test_the_retry_of_an_in_flight_409_carries_the_first_attempts_key(client_class: type, call: Call) -> None:
    """The retry of an in-flight 409 sends the key the SDK made for the first attempt again, so the server answers the
    first call's result instead of starting a second."""
    script = Script([limits_read(), call.refused("idempotency-key-in-flight", 409, retry_after=1), call.answered()])

    await settle(call.on(script.client_for(client_class)))

    keys = keys_sent(script, call)
    assert len(keys) == 2 and is_uuid4(keys[0]), f"two attempts, the first with a UUID v4 key: {keys}"
    assert keys[1] == keys[0], f"the retry carries the first attempt's key: {keys}"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
async def test_the_key_the_sdk_made_stays_through_every_retried_answer(clock: Clock, client_class: type) -> None:
    """A 429, then an in-flight 409, then the answer: the three attempts carry the one key the SDK made, each retry
    after the wait its answer asked for."""
    script = Script(
        [
            limits_read(),
            FETCH.refused("rate-limit-exceeded", 429, retry_after=3),
            FETCH.refused("idempotency-key-in-flight", 409, retry_after=2),
            FETCH.answered(),
        ]
    )

    await settle(FETCH.on(script.client_for(client_class)))

    keys = keys_sent(script, FETCH)
    assert len(keys) == 3 and is_uuid4(keys[0]) and set(keys) == {keys[0]}, f"one key on all three attempts: {keys}"
    assert clock.waits == [3, 2], f"each retry after the wait its answer asked for: {clock.waits}"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("call", FREE_READS, ids=ids(FREE_READS))
async def test_a_read_or_the_delete_goes_out_alone_with_no_key(client_class: type, call: Call) -> None:
    """A call that never bills goes out alone, with no key and under the client's own timeout: no limits are read before
    it and nothing is set on it."""
    script = Script([call.answered()])

    await settle(call.on(script.client_for(client_class)))

    assert [(r.method, r.url.path) for r in script.requests] == [(call.http_method, call.path)], "no limits read first"
    (request,) = script.requests
    assert "Idempotency-Key" not in request.headers, "no key on a call that never bills"
    assert request.extensions["timeout"] == CLIENT_TIMEOUT.as_dict(), (
        "a call that never bills keeps the client's timeout"
    )
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("call", FREE_POSTS, ids=ids(FREE_POSTS))
async def test_the_two_free_posts_go_out_with_nothing_of_the_clients_own(
    monkeypatch: pytest.MonkeyPatch, client_class: type, call: Call
) -> None:
    """cancel_job and compare_contents bill nothing. On a client built with no timeout of the caller's, a free POST goes
    out with no limits read before it; and once a call that may bill has read the limits, whose bound gives that call a
    timeout of its own, a free POST still goes out under the timeout a read gets, not the one the limits gave."""
    read = FREE_READS[0]
    script = Script([call.answered(), limits_read(), FETCH.answered(), call.answered(), read.answered()])
    client = script.default_client(client_class, monkeypatch)

    await settle(call.on(client))
    await settle(FETCH.on(client))
    await settle(call.on(client))
    await settle(read.on(client))

    assert [(r.method, r.url.path) for r in script.requests] == [
        (call.http_method, call.path),
        ("GET", "/v1/limits"),
        (FETCH.http_method, FETCH.path),
        (call.http_method, call.path),
        (read.http_method, read.path),
    ], "no limits read before a call that never bills; the one read comes before the call that may bill"
    before, _, billed, after, of_a_read = (request.extensions["timeout"] for request in script.requests)
    assert billed != of_a_read, f"the limits gave the call that may bill a timeout of its own: {billed}, {of_a_read}"
    assert before == after == of_a_read, (
        f"a free POST goes out under the timeout a read gets, before and after the limits are read: {before}, {after}"
    )
    assert script.unexpected == [], f"only the requests the calls call for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("call", FREE_POSTS, ids=ids(FREE_POSTS))
async def test_an_error_a_free_post_raises_carries_no_key_of_the_clients_making(client_class: type, call: Call) -> None:
    """A free POST refused 404 raises the typed error with no `idempotency_key` on it: the client makes no key for a
    call that never bills."""
    which_id = "job_id" if call.method == "cancel_job" else "baseline_contents_id"
    script = Script([call.refused("not-found", 404, change={"field": which_id})])

    with pytest.raises(NotFoundError) as raised:
        await settle(call.on(script.client_for(client_class)))

    assert not hasattr(raised.value, "idempotency_key"), "no key of the client's own on a call that never bills"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("key", ["made by the SDK", "the caller's own"])
@pytest.mark.parametrize("call", BILLED_CALLS, ids=ids(BILLED_CALLS))
async def test_a_refusal_of_a_billed_call_carries_the_key_it_went_out_under(
    client_class: type, call: Call, key: str
) -> None:
    """The typed error a refused call that may bill raises, here a 401, carries as `idempotency_key` the key the call
    went out under, the caller's own when one was given and the one the SDK made otherwise, so a repeat of the call is a
    replay."""
    script = Script([limits_read(), call.refused("unauthorized", 401)])
    given = {"idempotency_key": CALLERS_KEY} if key == "the caller's own" else {}

    with pytest.raises(UnauthorizedError) as raised:
        await settle(call.on(script.client_for(client_class), **given))

    (sent,) = keys_sent(script, call)
    assert (sent == CALLERS_KEY) if given else is_uuid4(sent), f"the caller's key when given, else a UUID v4: {sent}"
    assert getattr(raised.value, "idempotency_key", None) == sent, "the error carries the key the call went out under"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


def overloaded(call: Call) -> typing.List[typing.Union[Answer, Failure]]:
    """A 503 on all five attempts, each asking a wait of 1 second."""
    return [call.refused("overloaded", 503, retry_after=1) for _ in range(5)]


def no_answer(call: Call) -> typing.List[typing.Union[Answer, Failure]]:
    """The connection refused on all five attempts."""
    return [Failure(call.http_method, call.path, httpx.ConnectError("connection refused")) for _ in range(5)]


def timed_out(call: Call) -> typing.List[typing.Union[Answer, Failure]]:
    """An attempt whose answer did not come within its timeout, which is not retried, since the server may have done
    the work."""
    return [Failure(call.http_method, call.path, httpx.ReadTimeout("the answer did not come within the timeout"))]


FAILURES = [(overloaded, ServiceUnavailableError), (no_answer, httpx.ConnectError), (timed_out, httpx.ReadTimeout)]


@CLIENTS
@pytest.mark.parametrize("call", BILLED_CALLS, ids=ids(BILLED_CALLS))
@pytest.mark.parametrize("failure, error_class", FAILURES, ids=["503 on every attempt", "no answer", "a timeout"])
async def test_a_failure_of_a_billed_call_carries_the_key_every_attempt_carried(
    client_class: type,
    call: Call,
    failure: typing.Callable[[Call], typing.List[typing.Union[Answer, Failure]]],
    error_class: typing.Type[Exception],
) -> None:
    """The error a call that may bill raises after a 503 on every attempt, after no answer at all, or after a timeout
    carries as `idempotency_key` the one key the SDK made, which every attempt carried, so the caller's own repeat is a
    replay and never a second charge."""
    script = Script([limits_read(), *failure(call)])

    with pytest.raises(error_class) as raised:
        await settle(call.on(script.client_for(client_class)))

    keys = set(keys_sent(script, call))
    assert len(keys) == 1, f"one key on every attempt: {keys}"
    (sent,) = keys
    assert is_uuid4(sent), f"the key the SDK made: {sent}"
    assert getattr(raised.value, "idempotency_key", None) == sent, "the error carries the key every attempt carried"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"
