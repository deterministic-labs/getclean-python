"""The in-flight 409 and the one count of attempts. A 409 whose problem type is idempotency-key-in-flight is retried
after the server's wait when it is within 30 seconds, else after a backoff from one second that doubles and never passes
30; a wait past 30 seconds ends the retries with the answer as it arrived; every other 409 is raised at once. The
in-flight 409 and the 429, 502, 503 and 504 share one count of five attempts per call, which the caller's max_retries
governs, and the in-flight 409 raised when the retries end carries the key the attempts went out under."""

import json
import typing

import pytest
from ._support import (
    CLIENTS,
    FETCH,
    HIGHLIGHT,
    PROBLEM_TYPE_BASE,
    SUMMARIZE,
    Answer,
    Call,
    Clock,
    Script,
    clock,
    limits_read,
    pin_draws,
    request_id,
    settle,
)

from getclean.errors import (
    BadGatewayError,
    ConflictError,
    GatewayTimeoutError,
    ServiceUnavailableError,
    TooManyRequestsError,
)
from getclean.types.problem import Problem

# Every test of this file runs with time stood in, so that none waits for real, even on a client that waits
# where it should not.
pytestmark = pytest.mark.usefixtures(clock.__name__)

CALLERS_KEY = "order-7-fetch"
"""An idempotency key a caller gives a call."""


def in_flight(retry_after: typing.Optional[int], label: str = "") -> Answer:
    """fetch_contents refused 409 idempotency-key-in-flight, with the server's wait when given, as Retry-After and as
    the body's retry_after_seconds, which the contract makes equal; its request id named by the label when one is
    given."""
    return FETCH.refused("idempotency-key-in-flight", 409, retry_after, request_id=request_id(label))


@CLIENTS
async def test_an_in_flight_409_is_retried_after_the_wait_the_server_asks(clock: Clock, client_class: type) -> None:
    """An in-flight 409 with Retry-After: 2 is retried after one wait of 2 seconds, and the call returns the answer that
    follows."""
    answer = FETCH.answered()
    script = Script([limits_read(), in_flight(2), answer])

    contents = await settle(FETCH.on(script.client_for(client_class)))

    assert clock.waits == [2], f"one wait, the 2 seconds the server asked for: {clock.waits}"
    assert contents.request_id == answer.body["request_id"], "the call returns the answer after the retry"
    assert len(script.sent("POST", "/v1/contents")) == 2, "one retry"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
async def test_a_wait_of_30_seconds_is_honored_as_sent(clock: Clock, client_class: type) -> None:
    """A Retry-After of 30 seconds, the most the client waits, is waited as sent."""
    answer = FETCH.answered()
    script = Script([limits_read(), in_flight(30), answer])

    contents = await settle(FETCH.on(script.client_for(client_class)))

    assert clock.waits == [30], f"a wait of 30 seconds is waited as sent: {clock.waits}"
    assert contents.request_id == answer.body["request_id"], "the call returns the answer after the retry"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
async def test_a_wait_past_30_seconds_ends_the_retries_with_the_answer_as_it_arrived(
    clock: Clock, client_class: type
) -> None:
    """A Retry-After of 31 seconds, past the most the client waits, is not waited: the 409 is raised as it arrived, its
    retry_after_seconds on its body and its Retry-After on its headers, for the caller to decide."""
    answer = in_flight(31)
    script = Script([limits_read(), answer])

    with pytest.raises(ConflictError) as raised:
        await settle(FETCH.on(script.client_for(client_class)))

    assert clock.waits == [], f"no wait past 30 seconds: {clock.waits}"
    assert len(script.sent("POST", "/v1/contents")) == 1, "no retry when the server's wait passes 30 seconds"
    assert isinstance(raised.value.body, Problem) and raised.value.body.retry_after_seconds == 31, (
        "the server's wait is readable on the error's body"
    )
    assert json.loads(raised.value.body.json()) == answer.body, "the problem as it arrived, member for member"
    assert raised.value.headers is not None and raised.value.headers["retry-after"] == "31", (
        "the server's wait is readable on the error's headers"
    )
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


BACKOFF = [1, 2, 4, 8, 16, 32]
"""The backoff's nominal waits between seven attempts: from 1 second, doubling."""


@CLIENTS
@pytest.mark.parametrize("end", ["lowest", "highest"])
async def test_without_a_wait_from_the_server_the_backoff_doubles_from_one_second_and_never_passes_30(
    clock: Clock, monkeypatch: pytest.MonkeyPatch, client_class: type, end: str
) -> None:
    """In-flight 409s with no wait from the server are retried after a backoff: with max_retries 6, the six waits
    between seven attempts start at 1 second and double, the random draw pinned at either end of its range bracketing 1,
    2, 4, 8, 16 and 32 seconds from that end's side, and none passes 30."""
    pin_draws(monkeypatch, end)
    script = Script([limits_read(), *[in_flight(None) for _ in range(6)], FETCH.answered()])

    await settle(FETCH.on(script.client_for(client_class), request_options={"max_retries": 6}))

    waits = clock.waits
    assert len(waits) == 6 and len(script.sent("POST", "/v1/contents")) == 7, f"a wait before each retry: {waits}"
    if end == "lowest":
        assert all(wait <= value for wait, value in zip(waits, BACKOFF)), f"at or under 1, 2, 4, 8, 16, 32: {waits}"
    else:
        assert all(wait >= min(value, 30) for wait, value in zip(waits, BACKOFF)), f"at or over each, to 30: {waits}"
    assert all(waits[n + 1] == pytest.approx(2 * waits[n]) for n in range(4)), f"the backoff doubles: {waits}"
    assert max(waits) <= 30, f"no wait passes 30 seconds: {waits}"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
async def test_five_in_flight_answers_end_with_the_fifth_raised(clock: Clock, client_class: type) -> None:
    """Five in-flight 409s in a row make five attempts, a wait before each retry, and the fifth answer is raised."""
    answers = [in_flight(1, label=f"InFlight{n}") for n in range(1, 6)]
    script = Script([limits_read(), *answers])

    with pytest.raises(ConflictError) as raised:
        await settle(FETCH.on(script.client_for(client_class)))

    assert len(script.sent("POST", "/v1/contents")) == 5, "five attempts"
    assert clock.waits == [1, 1, 1, 1], f"a wait before each of the four retries: {clock.waits}"
    assert raised.value.body.request_id == request_id("InFlight5"), "the fifth answer is the one raised"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("key", ["made by the SDK", "the caller's own"])
@pytest.mark.parametrize("ending", ["past the most the client waits", "after five attempts"])
async def test_an_in_flight_409_raised_carries_the_key_its_attempts_went_out_under(
    client_class: type, ending: str, key: str
) -> None:
    """The in-flight 409 raised when the retries end, at a wait past 30 seconds or after five attempts, carries as
    `idempotency_key` the key every attempt went out under, the caller's own when one was given and the one the SDK made
    otherwise, so the caller who waits and asks again replays the first call instead of starting a second."""
    answers = [in_flight(31)] if ending == "past the most the client waits" else [in_flight(1) for _ in range(5)]
    script = Script([limits_read(), *answers])
    given = {"idempotency_key": CALLERS_KEY} if key == "the caller's own" else {}

    with pytest.raises(ConflictError) as raised:
        await settle(FETCH.on(script.client_for(client_class), **given))

    keys = {request.headers["Idempotency-Key"] for request in script.sent("POST", "/v1/contents")}
    assert len(keys) == 1, f"every attempt went out under one key: {keys}"
    (sent_key,) = keys
    assert not given or sent_key == CALLERS_KEY, "the attempts went out under the caller's key when one was given"
    assert getattr(raised.value, "idempotency_key", None) == sent_key, (
        "the 409 raised carries the key it went out under"
    )
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
async def test_a_record_without_content_409_is_raised_at_once(clock: Clock, client_class: type) -> None:
    """A 409 record-without-content is never retried: it is raised at once, after one request."""
    refusal = HIGHLIGHT.refused("record-without-content", 409)
    script = Script([limits_read(), refusal])

    with pytest.raises(ConflictError) as raised:
        await settle(HIGHLIGHT.on(script.client_for(client_class)))

    assert len(script.sent("POST", HIGHLIGHT.path)) == 1 and clock.waits == [], "raised at once, with no retry"
    assert json.loads(raised.value.body.json()) == refusal.body, "the problem as it arrived"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
async def test_a_409_of_a_type_this_contract_does_not_give_is_raised_at_once_though_its_name_ends_like_in_flight(
    clock: Clock, client_class: type
) -> None:
    """A 409 is retried only when its type's last segment is idempotency-key-in-flight, the segment that names a type; a
    type this version does not know, whose name merely ends with those words, is raised at once."""
    other = FETCH.refused(
        "idempotency-key-in-flight",
        409,
        type=PROBLEM_TYPE_BASE + "stale-idempotency-key-in-flight",
        title="A stale idempotency key is in flight",
        detail="A stale idempotency key is in flight.",
    )
    script = Script([limits_read(), other])

    with pytest.raises(ConflictError):
        await settle(FETCH.on(script.client_for(client_class)))

    assert len(script.sent("POST", "/v1/contents")) == 1 and clock.waits == [], "raised at once, with no retry"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


RETRIED_STATUSES = [
    # (status, problem type, the call it may answer, the server's wait, the error class a caller catches). A 429 and a
    # 503 always ask for a wait; a 502 and a 504 ask for none and answer only a model step that is the whole call, as
    # summarize_contents is.
    (429, "rate-limit-exceeded", FETCH, 1, TooManyRequestsError),
    (503, "overloaded", FETCH, 1, ServiceUnavailableError),
    (502, "gateway-error", SUMMARIZE, None, BadGatewayError),
    (504, "gateway-timeout", SUMMARIZE, None, GatewayTimeoutError),
]


@CLIENTS
@pytest.mark.parametrize(
    "status, type_name, call, retry_after",
    [case[:4] for case in RETRIED_STATUSES],
    ids=["429", "503", "502", "504"],
)
async def test_a_429_502_503_or_504_then_the_answer_costs_one_retry_and_one_wait(
    clock: Clock, client_class: type, status: int, type_name: str, call: Call, retry_after: typing.Optional[int]
) -> None:
    """A 429, 502, 503 or 504, then the answer: one retry after one wait, the server's when it asked for one, and the
    call returns the answer."""
    answer = call.answered()
    script = Script([limits_read(), call.refused(type_name, status, retry_after), answer])

    result = await settle(call.on(script.client_for(client_class)))

    assert len(script.sent("POST", call.path)) == 2, "one retry"
    assert len(clock.waits) == 1, f"one wait before the retry: {clock.waits}"
    assert retry_after is None or clock.waits == [retry_after], f"the server's wait when it asked one: {clock.waits}"
    assert result.request_id == answer.body["request_id"], "the call returns the answer after the retry"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize(
    "status, type_name, call, retry_after, error_class", RETRIED_STATUSES, ids=["429", "503", "502", "504"]
)
async def test_five_429s_502s_503s_or_504s_end_with_the_fifth_raised(
    clock: Clock,
    client_class: type,
    status: int,
    type_name: str,
    call: Call,
    retry_after: typing.Optional[int],
    error_class: type,
) -> None:
    """Five 429s, 502s, 503s or 504s make five attempts and four waits, then the typed error of the status is raised
    with the fifth answer; no sixth request leaves."""
    refusals = [call.refused(type_name, status, retry_after, request_id=request_id(f"Refusal{n}")) for n in range(1, 6)]
    script = Script([limits_read(), *refusals])

    with pytest.raises(error_class) as raised:
        await settle(call.on(script.client_for(client_class)))

    assert len(script.sent("POST", call.path)) == 5, "five attempts and no sixth"
    assert len(clock.waits) == 4, f"a wait before each of the four retries: {clock.waits}"
    assert typing.cast(typing.Any, raised.value).body.request_id == request_id("Refusal5"), "the fifth answer is raised"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


def refused(type_name: str, status: int, label: str) -> Answer:
    """fetch_contents refused with a problem a retry can help, the server asking a wait of 1 second, the request id
    named by the label."""
    return FETCH.refused(type_name, status, 1, request_id=request_id(label))


@CLIENTS
async def test_one_count_of_five_attempts_covers_every_retried_answer(clock: Clock, client_class: type) -> None:
    """A 429, an in-flight 409, a 503, an in-flight 409 and a 429 again are the five attempts of one call: the fifth
    answer is raised and no sixth request leaves, since one count covers every answer that is retried."""
    answers = [
        refused("rate-limit-exceeded", 429, "Refusal1"),
        refused("idempotency-key-in-flight", 409, "Refusal2"),
        refused("overloaded", 503, "Refusal3"),
        refused("idempotency-key-in-flight", 409, "Refusal4"),
        refused("rate-limit-exceeded", 429, "Refusal5"),
    ]
    script = Script([limits_read(), *answers])

    with pytest.raises(TooManyRequestsError) as raised:
        await settle(FETCH.on(script.client_for(client_class)))

    assert len(script.sent("POST", "/v1/contents")) == 5, "five attempts in one count, not five of each kind"
    assert raised.value.body.request_id == request_id("Refusal5"), "the fifth answer is the one raised"
    assert clock.waits == [1, 1, 1, 1], f"a wait before each of the four retries: {clock.waits}"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


MAX_RETRIES_CASES = [
    # (max_retries, the answers the call meets, the attempts it makes): the count is max_retries plus the first attempt.
    (0, [("idempotency-key-in-flight", 409)], 1),
    (2, [("idempotency-key-in-flight", 409), ("overloaded", 503), ("idempotency-key-in-flight", 409)], 3),
]


@CLIENTS
@pytest.mark.parametrize("given_to", ["the call", "the client"])
@pytest.mark.parametrize("max_retries, kinds, attempts", MAX_RETRIES_CASES, ids=["max_retries 0", "max_retries 2"])
async def test_the_callers_max_retries_governs_the_one_count(
    clock: Clock,
    client_class: type,
    given_to: str,
    max_retries: int,
    kinds: typing.List[typing.Tuple[str, int]],
    attempts: int,
) -> None:
    """A caller's max_retries, given to the call or to the client, governs the one count, in-flight 409s included: 0
    raises the first in-flight 409 after one attempt and no wait; 2 raises the third of three answers."""
    answers = [refused(type_name, status, f"Refusal{n}") for n, (type_name, status) in enumerate(kinds, start=1)]
    script = Script([limits_read(), *answers])
    on_the_call = {"request_options": {"max_retries": max_retries}} if given_to == "the call" else {}
    client = script.client_for(client_class, **({} if on_the_call else {"max_retries": max_retries}))

    with pytest.raises(ConflictError) as raised:
        await settle(FETCH.on(client, **on_the_call))

    assert len(script.sent("POST", "/v1/contents")) == attempts, f"{attempts} attempts under max_retries {max_retries}"
    assert raised.value.body.request_id == request_id(f"Refusal{attempts}"), "the last answer is the one raised"
    assert len(clock.waits) == attempts - 1, f"a wait before each retry and no other: {clock.waits}"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"
