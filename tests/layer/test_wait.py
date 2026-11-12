"""The upload's wait. Off by default: the answer as it comes. With wait=True the job is polled with get_job until it is
final, then its record is read under the upload's own options, or its failure is raised as a typed error; a job not
finished at the bound comes back as it stands. The polls and the read run under options of their own, are tried again
after a 429, a 5xx or no answer within the bound, after the server's wait or a backoff from one second, and end at a
4xx. Every error the wait raises carries the last job seen and the upload's idempotency key."""

import json
import typing

import httpx
import pytest
from ._support import (
    CLIENT_TIMEOUT,
    CLIENTS,
    DOCUMENT,
    JOB_ID,
    JOB_SECONDS,
    PROBLEM_TABLE,
    PROBLEM_TYPE_BASE,
    UPLOAD,
    UPLOAD_CALL,
    UPLOAD_REQUEST_ID,
    Answer,
    Body,
    Clock,
    Failure,
    Script,
    accepted,
    canceled_record,
    canceled_with_pages,
    canceled_without_record,
    clock,
    completed,
    example,
    failed_record,
    failed_with_record,
    failed_without_record,
    job_problem,
    limits_read,
    per_attempt,
    pin_draws,
    polled,
    queued,
    read_of,
    refusal,
    request_id,
    settle,
    the_record,
    under_request_id,
)

from getclean import ApiError, JobCanceled
from getclean.core.pydantic_utilities import parse_obj_as
from getclean.errors import (
    ContentTooLargeError,
    ForbiddenError,
    GoneError,
    InternalServerError,
    NotFoundError,
    ServiceUnavailableError,
    UnavailableForLegalReasonsError,
    UnprocessableEntityError,
)
from getclean.types.contents import Contents
from getclean.types.contents_upload import ContentsUpload
from getclean.types.job import Job

# Every test of this file runs with time stood in, so that none waits for real, even on a client that waits
# where it should not.
pytestmark = pytest.mark.usefixtures(clock.__name__)

POLL = f"/v1/jobs/{JOB_ID}"

POLL_WAIT_SECONDS = 60
"""The wait each poll asks get_job to hold the answer for: a minute."""

MARGIN_SECONDS = 10
"""What a poll's timeout adds to the wait it asks for, so the held answer has time to arrive."""

BOUND_SECONDS = JOB_SECONDS + 60
"""The wait's bound with the tests' limits: the contents job_seconds bound and one more minute."""

CALLERS_KEY = "minutes-upload-2026-11-04"
"""An idempotency key a caller gives the upload."""


async def upload(script: Script, client_class: type, **options: typing.Any) -> ContentsUpload:
    """upload_contents on the client of this class, the document as bytes, with the given options."""
    return await settle(script.client_for(client_class).upload_contents(document=DOCUMENT, **options))


def paths(script: Script) -> typing.List[typing.Tuple[str, str]]:
    return [(request.method, request.url.path) for request in script.requests]


@CLIENTS
@pytest.mark.parametrize("wait", [None, True], ids=["wait unset", "wait=True"])
async def test_a_201_comes_back_as_answered_with_no_poll(client_class: type, wait: typing.Optional[bool]) -> None:
    """An upload answered 201 returns ContentsUpload as the server gave it, whether wait is unset or set, and nothing is
    polled."""
    answer = UPLOAD_CALL.answered()
    script = Script([limits_read(), answer])

    result = await upload(script, client_class, **({} if wait is None else {"wait": wait}))

    assert result == parse_obj_as(ContentsUpload, answer.body), "a 201 comes back as it was answered"
    assert paths(script) == [("GET", "/v1/limits"), ("POST", UPLOAD)], "a 201 is never polled"
    assert script.unexpected == [], f"only the requests the upload calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("wait", [None, False], ids=["wait unset", "wait=False"])
async def test_a_202_without_wait_comes_back_as_answered_with_no_poll(
    client_class: type, wait: typing.Optional[bool]
) -> None:
    """An upload answered 202 without wait returns ContentsUpload with the job as the server gave it, and nothing is
    polled: the wait is off by default."""
    answer = accepted()
    script = Script([limits_read(), answer])

    result = await upload(script, client_class, **({} if wait is None else {"wait": wait}))

    assert result == parse_obj_as(ContentsUpload, answer.body), "a 202 without wait comes back as it was answered"
    assert paths(script) == [("GET", "/v1/limits"), ("POST", UPLOAD)], "without wait nothing is polled"
    assert script.unexpected == [], f"only the requests the upload calls for: {script.unexpected}"


@CLIENTS
async def test_wait_polls_the_job_to_its_end_then_reads_the_record_under_the_uploads_options(
    client_class: type,
) -> None:
    """With wait=True a 202's job is polled, each poll asking get_job to hold the answer 60 seconds, until the job is
    final; then its record is read with the upload's max_characters, formats and block_kinds and no scope. The result
    carries that record, the final job and the upload's own request id."""
    final = polled(completed())
    read = read_of(final.body, the_record())
    script = Script([limits_read(), accepted(queued()), polled(queued()), final, read])

    result = await upload(
        script,
        client_class,
        max_characters=5000,
        formats=["markdown", "json"],
        block_kinds=["text", "table"],
        wait=True,
    )

    polls = script.sent("GET", POLL)
    assert [list(poll.url.params.keys()) for poll in polls] == [["wait_seconds"]] * 2, (
        "each poll asks to wait, nothing else"
    )
    assert [float(poll.url.params["wait_seconds"]) for poll in polls] == [POLL_WAIT_SECONDS] * 2, (
        "each poll asks the server to hold the answer 60 seconds"
    )
    (sent,) = script.sent("GET", read.path)
    assert sorted(sent.url.params.multi_items()) == sorted(
        [
            ("max_characters", "5000"),
            ("formats", "markdown"),
            ("formats", "json"),
            ("block_kinds", "text"),
            ("block_kinds", "table"),
        ]
    ), "the record is read under the upload's own max_characters, formats and block_kinds, and no scope"
    assert result.contents == parse_obj_as(Contents, read.body), "the result carries the record as it was read"
    assert result.job == parse_obj_as(Job, final.body), "the result carries the final job"
    assert result.request_id == UPLOAD_REQUEST_ID, "the result carries the upload's own request id"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


@CLIENTS
async def test_the_read_sends_none_of_the_three_options_the_upload_did_not_send(client_class: type) -> None:
    """An upload that sent no max_characters, formats or block_kinds reads its record with none of them."""
    final = polled(completed())
    script = Script([limits_read(), accepted(queued()), final, read_of(final.body, the_record())])

    await upload(script, client_class, wait=True)

    (sent,) = script.sent("GET", f"/v1/contents/{final.body['contents_id']}")
    assert list(sent.url.params.multi_items()) == [], "the read carries only the options the upload sent"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


@CLIENTS
async def test_the_read_takes_only_the_lists_the_upload_sent(client_class: type) -> None:
    """An empty formats list on the upload, which a form cannot carry and a query refuses, does not reach the read,
    while the list the upload did send does."""
    final = polled(completed())
    script = Script([limits_read(), accepted(queued()), final, read_of(final.body, the_record())])

    await upload(script, client_class, formats=[], block_kinds=["text"], wait=True)

    (sent,) = script.sent("GET", f"/v1/contents/{final.body['contents_id']}")
    assert list(sent.url.params.multi_items()) == [("block_kinds", "text")], (
        "the read takes the lists the upload sent, and leaves out the empty one"
    )
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


ENDINGS_WITH_A_RECORD = {
    # The three endings that leave a record, each with the record the job names: completed; failed with a record, the
    # document having not opened; canceled with pages done, which are kept and billed.
    "completed": (completed, the_record),
    "failed with a record": (failed_with_record, failed_record),
    "canceled with pages done": (canceled_with_pages, canceled_record),
}


@CLIENTS
@pytest.mark.parametrize("ending", ENDINGS_WITH_A_RECORD.values(), ids=ENDINGS_WITH_A_RECORD.keys())
async def test_a_job_that_ends_with_a_record_returns_the_record_as_read(
    client_class: type, ending: typing.Tuple[typing.Callable[[], Body], typing.Callable[[], Body]]
) -> None:
    """A job that ended with a record, completed, failed with a record, or canceled with pages done, returns that record
    as the read gave it, with the final job and no error."""
    final_job, its_record = ending
    final = polled(final_job())
    read = read_of(final.body, its_record())
    script = Script([limits_read(), accepted(queued()), final, read])

    result = await upload(script, client_class, wait=True)

    assert result.contents == parse_obj_as(Contents, read.body), "a job that left a record returns the record as read"
    assert result.job == parse_obj_as(Job, final.body), "with the final job"
    assert result.request_id == UPLOAD_REQUEST_ID, "under the upload's own request id"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


JOB_PROBLEMS = [
    # Problem types a job that failed without a record may carry, each with the members its type carries and the error
    # class of the status it maps to: 403, 413, 422, 451 and 500, three of the types mapping to 422.
    ("credit-exhausted", ForbiddenError),
    ("body-too-large", ContentTooLargeError),
    ("invalid-field", UnprocessableEntityError),
    ("destination-refused", UnprocessableEntityError),
    ("cost-exceeds-cap", UnprocessableEntityError),
    ("legal-block", UnavailableForLegalReasonsError),
    ("internal-error", InternalServerError),
]


@CLIENTS
@pytest.mark.parametrize("type_name, error_class", JOB_PROBLEMS, ids=[name for name, _ in JOB_PROBLEMS])
async def test_a_job_failed_without_a_record_raises_the_error_class_of_its_problems_status(
    client_class: type, type_name: str, error_class: typing.Type[ApiError]
) -> None:
    """A job that failed with a problem and no record raises the error class of the status the contract's table gives
    the problem's type, with that status; the problem, which a job carries without a status, is the error's body as the
    job carried it."""
    failure = job_problem(type_name)
    script = Script([limits_read(), accepted(queued()), polled(failed_without_record(failure))])

    with pytest.raises(error_class) as raised:
        await upload(script, client_class, wait=True)

    assert type(raised.value) is error_class, "the class of the status the type maps to, not a base class"
    assert raised.value.status_code == PROBLEM_TABLE[type_name][0], "the status the contract's table gives the type"
    assert json.loads(raised.value.body.json()) == failure, "the job's problem is the error's body, as it came"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


def a_type_this_version_does_not_know() -> Body:
    """A problem of a type the contract's table does not name, as a later version may add one, its registry being open:
    the title and the detail are that type's own."""
    failure = job_problem("internal-error")
    failure.update(
        type=PROBLEM_TYPE_BASE + "a-type-this-version-does-not-know",
        title="A type this version does not know",
        detail="A type this version does not know.",
    )
    return failure


@CLIENTS
async def test_a_job_failed_with_a_type_this_contract_does_not_give_raises_the_base_error(client_class: type) -> None:
    """A job that failed with a problem of a type this version does not know raises ApiError itself, the problem on
    it, since the type maps to no status this version knows."""
    failure = a_type_this_version_does_not_know()
    script = Script([limits_read(), accepted(queued()), polled(failed_without_record(failure))])

    with pytest.raises(ApiError) as raised:
        await upload(script, client_class, wait=True)

    assert type(raised.value) is ApiError, "an unknown type raises the base error class"
    assert json.loads(raised.value.body.json()) == failure, "the job's problem is the error's body, as it came"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


@CLIENTS
async def test_a_job_canceled_without_a_record_raises_job_canceled_carrying_the_job(client_class: type) -> None:
    """A job canceled before any page was done, with no record, raises JobCanceled carrying the final job, its message
    naming the job."""
    final = polled(canceled_without_record())
    script = Script([limits_read(), accepted(queued()), final])

    with pytest.raises(JobCanceled) as raised:
        await upload(script, client_class, wait=True)

    assert raised.value.job == parse_obj_as(Job, final.body), "JobCanceled carries the final job"
    assert JOB_ID in str(raised.value), "JobCanceled's message names the job"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


def ending_with_an_error(name: str) -> typing.Tuple[typing.List[typing.Union[Answer, Failure]], type, Body]:
    """The answers after the upload's 202 that end the wait with an error, the error's class, and the last job seen."""
    if name == "a poll refused 404":
        last = polled(queued())
        return [last, refusal("GET", POLL, "not-found", 404)], NotFoundError, last.body
    if name == "the read refused 410":
        last = polled(completed())
        gone = under_request_id(example("get_contents.contents-expired"), request_id())
        return [last, Answer("GET", f"/v1/contents/{last.body['contents_id']}", 410, gone)], GoneError, last.body
    if name == "a job failed without a record":
        last = polled(failed_without_record(job_problem("internal-error")))
        return [last], InternalServerError, last.body
    if name == "a job failed with a type the table lacks":
        last = polled(failed_without_record(a_type_this_version_does_not_know()))
        return [last], ApiError, last.body
    last = polled(canceled_without_record())
    return [last], JobCanceled, last.body


ERROR_ENDINGS = [
    "a poll refused 404",
    "the read refused 410",
    "a job failed without a record",
    "a job failed with a type the table lacks",
    "a job canceled without a record",
]


@CLIENTS
@pytest.mark.parametrize("ending", ERROR_ENDINGS)
async def test_an_error_the_wait_raises_carries_the_last_job_seen(client_class: type, ending: str) -> None:
    """Every error the wait raises, a poll's or the read's refusal, a failed job's problem or JobCanceled, carries the
    last job seen as `job`, so the caller holds the job's id and can read it later."""
    answers, error_class, last_job = ending_with_an_error(ending)
    script = Script([limits_read(), accepted(queued()), *answers])

    with pytest.raises(error_class) as raised:
        await upload(script, client_class, wait=True)

    assert getattr(raised.value, "job", None) == parse_obj_as(Job, last_job), "the error carries the last job seen"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("key", ["made by the SDK", "the caller's own"])
@pytest.mark.parametrize("ending", ERROR_ENDINGS)
async def test_an_error_the_wait_raises_carries_the_uploads_idempotency_key(
    client_class: type, ending: str, key: str
) -> None:
    """Every error the wait raises carries the upload's idempotency key as `idempotency_key`, the caller's own when one
    was given and the one the SDK made otherwise, so that repeating the upload replays it and never bills twice."""
    answers, error_class, _ = ending_with_an_error(ending)
    script = Script([limits_read(), accepted(queued()), *answers])
    given = {"idempotency_key": CALLERS_KEY} if key == "the caller's own" else {}

    with pytest.raises(error_class) as raised:
        await upload(script, client_class, wait=True, **given)

    sent_key = script.sent("POST", UPLOAD)[0].headers["Idempotency-Key"]
    assert not given or sent_key == CALLERS_KEY, "the upload went out under the caller's key when one was given"
    assert getattr(raised.value, "idempotency_key", None) == sent_key, (
        "an error the upload's wait raises carries the key the upload went out under"
    )
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


@CLIENTS
async def test_a_job_not_finished_at_the_bound_comes_back_as_it_stands(clock: Clock, client_class: type) -> None:
    """A job not finished once the bound, the limits' job_seconds and one more minute, has passed comes back as it
    stands, with no error, and the polls stop there: with job_seconds 1200 and each poll held its 60 seconds, 21 polls,
    at 0, 60 and on to 1200 seconds."""
    polls = [polled(queued()) for _ in range(21)]
    script = Script([limits_read(), accepted(queued()), *polls], clock=clock)

    result = await upload(script, client_class, wait=True)

    assert len(script.sent("GET", POLL)) == 21 and script.unanswered == [], "the polls stop at the bound, 21 of them"
    assert clock.now == BOUND_SECONDS, f"the last poll ended at the bound: {clock.now}"
    assert result.contents is None, "a job not finished at the bound has no record to return"
    assert result.job == parse_obj_as(Job, polls[-1].body), "the job comes back as the last poll read it"
    assert result.request_id == UPLOAD_REQUEST_ID, "under the upload's own request id"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


@CLIENTS
async def test_until_the_limits_are_read_the_bound_is_31_minutes(clock: Clock, client_class: type) -> None:
    """When the limits could not be read, the bound is 30 minutes and one more: 31 polls held 60 seconds each, at 0, 60
    and on to 1800 seconds."""
    polls = [polled(queued()) for _ in range(31)]
    unread = refusal("GET", "/v1/limits", "internal-error", 500)
    script = Script([unread, accepted(queued()), *polls], clock=clock)

    result = await upload(script, client_class, wait=True)

    assert len(script.sent("GET", POLL)) == 31 and script.unanswered == [], "31 polls, then the bound of 31 minutes"
    assert result.job == parse_obj_as(Job, polls[-1].body), "the job comes back as the last poll read it"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


TRACEPARENT = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
"""A caller's header, the example of the W3C Trace Context recommendation."""


@CLIENTS
async def test_the_polls_run_under_their_own_timeout_and_keep_the_callers_headers(client_class: type) -> None:
    """A short timeout the caller gives the upload governs the upload alone: each poll, which asks the server to hold it
    60 seconds, runs under that wait plus 10 seconds, and the record's read under the client's own timeout; the
    caller's headers go on every one."""
    final = polled(completed())
    script = Script([limits_read(), accepted(queued()), polled(queued()), final, read_of(final.body, the_record())])

    await upload(
        script,
        client_class,
        wait=True,
        request_options={"timeout": 3, "additional_headers": {"traceparent": TRACEPARENT}},
    )

    (sent,) = script.sent("POST", UPLOAD)
    polls = script.sent("GET", POLL)
    (read,) = script.sent("GET", f"/v1/contents/{final.body['contents_id']}")
    assert sent.extensions["timeout"] == per_attempt(3), "the caller's timeout governs the upload itself"
    assert [poll.extensions["timeout"] for poll in polls] == [per_attempt(POLL_WAIT_SECONDS + MARGIN_SECONDS)] * 2, (
        "each poll runs under the wait it asks for plus 10 seconds"
    )
    assert read.extensions["timeout"] == CLIENT_TIMEOUT.as_dict(), "the read runs under the client's own timeout"
    assert [r.headers.get("traceparent") for r in [sent, *polls, read]] == [TRACEPARENT] * 4, (
        "the caller's headers go on the upload, every poll and the read"
    )
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


@CLIENTS
async def test_the_polls_and_the_read_carry_none_of_the_uploads_query_or_body_options(client_class: type) -> None:
    """The polls and the read carry the caller's headers and none of the upload's query or body options."""
    final = polled(completed())
    script = Script([limits_read(), accepted(queued()), polled(queued()), final, read_of(final.body, the_record())])
    options = {
        "additional_headers": {"traceparent": TRACEPARENT},
        "additional_query_parameters": {"trace": "on"},
        "additional_body_parameters": {"note": "for the upload alone"},
    }

    await upload(script, client_class, wait=True, request_options=options)

    later = [*script.sent("GET", POLL), *script.sent("GET", f"/v1/contents/{final.body['contents_id']}")]
    assert [r.headers.get("traceparent") for r in later] == [TRACEPARENT] * 3, "the caller's headers on each"
    assert [r.url.params.get("trace") for r in later] == [None] * 3, "none of the upload's query options"
    assert [r.content for r in later] == [b""] * 3, "none of the upload's body options"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


def two_rounds_asking_a_wait(method: str, path: str, type_name: str, status: int) -> typing.List[Answer]:
    """Ten refusals at this status, each one attempt of a poll or the read: in each five, the first four ask a wait of 1
    second and the fifth a wait of 2, so every wait tells which refusal it followed."""
    one_round = [refusal(method, path, type_name, status, retry_after=1) for _ in range(4)]
    return [*one_round, refusal(method, path, type_name, status, retry_after=2)] * 2


ASKING_A_WAIT = {"503": ("overloaded", 503), "429": ("rate-limit-exceeded", 429)}


@CLIENTS
@pytest.mark.parametrize("refused", ASKING_A_WAIT.values(), ids=ASKING_A_WAIT.keys())
@pytest.mark.parametrize("where", ["a poll", "the read"])
async def test_a_poll_or_the_read_refused_with_a_wait_is_tried_again_after_the_servers_wait(
    clock: Clock, client_class: type, where: str, refused: typing.Tuple[str, int]
) -> None:
    """A poll or the read refused 503 or 429 ten times over, each refusal one attempt, is tried again each time after
    the wait the server asked for, within the bound, and the wait goes on to the record: every wait is the server's,
    1 second after four of each five refusals and 2 after the fifth."""
    final = polled(completed())
    read = read_of(final.body, the_record())
    target = POLL if where == "a poll" else read.path
    refusals = two_rounds_asking_a_wait("GET", target, *refused)
    steps = [*refusals, final, read] if where == "a poll" else [final, *refusals, read]
    script = Script([limits_read(), accepted(queued()), *steps], clock=clock)

    result = await upload(script, client_class, wait=True)

    assert clock.waits == [1, 1, 1, 1, 2] * 2, f"each wait is the one the server asked for: {clock.waits}"
    assert len(script.sent("GET", target)) == 11, "ten refusals, each one attempt, then the answer"
    assert result.contents == parse_obj_as(Contents, read.body), "the wait goes on to the record"
    assert script.unexpected == [] and script.unanswered == [], (
        f"only the requests the wait calls for: {script.unexpected}"
    )


def bracketed(waits: typing.Sequence[float], nominal: typing.Sequence[float], end: str) -> bool:
    """Whether each wait lies on the pinned end's side of its nominal value: at or under it with the draw at its lowest,
    at or over it with the draw at its highest, a wait the cap holds at 30 being at most 30 either way."""
    if end == "lowest":
        return all(wait <= value for wait, value in zip(waits, nominal, strict=True))
    return all(wait >= min(value, 30) for wait, value in zip(waits, nominal, strict=True))


@CLIENTS
@pytest.mark.parametrize("end", ["lowest", "highest"])
@pytest.mark.parametrize("where", ["a poll", "the read"])
async def test_a_poll_or_the_read_with_no_answer_is_tried_again_after_a_backoff_from_one_second(
    clock: Clock, monkeypatch: pytest.MonkeyPatch, client_class: type, where: str, end: str
) -> None:
    """A poll or the read whose connection is refused ten times over is tried again after a backoff from 1 second that
    doubles with each try and never passes 30, each try one attempt, and the wait goes on to the record. With the random
    draw pinned at either end, the ten waits bracket 1, 2, 4, 8, 16, then 30 five times, and the first five double."""
    pin_draws(monkeypatch, end)
    final = polled(completed())
    read = read_of(final.body, the_record())
    target = POLL if where == "a poll" else read.path
    no_answer = [Failure("GET", target, httpx.ConnectError("connection refused")) for _ in range(10)]
    steps: typing.List[typing.Union[Answer, Failure]] = (
        [*no_answer, final, read] if where == "a poll" else [final, *no_answer, read]
    )
    script = Script([limits_read(), accepted(queued()), *steps], clock=clock)

    result = await upload(script, client_class, wait=True)

    waits = clock.waits
    assert len(waits) == 10, f"one wait between each of the ten tries and the next: {waits}"
    assert bracketed(waits, [1, 2, 4, 8, 16, 30, 30, 30, 30, 30], end), f"each wait brackets its backoff: {waits}"
    assert all(later == pytest.approx(2 * earlier) for earlier, later in zip(waits[0:4], waits[1:5])), (
        f"the first waits double: {waits}"
    )
    assert max(waits) <= 30, f"no wait passes 30 seconds: {waits}"
    assert result.contents == parse_obj_as(Contents, read.body), "the wait goes on to the record"
    assert script.unexpected == [] and script.unanswered == [], (
        f"only the requests the wait calls for: {script.unexpected}"
    )


@CLIENTS
@pytest.mark.parametrize("end", ["lowest", "highest"])
async def test_a_poll_answered_500_is_tried_again_after_a_backoff_that_never_passes_30_seconds(
    clock: Clock, monkeypatch: pytest.MonkeyPatch, client_class: type, end: str
) -> None:
    """A poll answered 500, which no call retries on its own, is tried again by the wait, since a job read is free and
    repeats without harm: six refusals in a row, then the job. The waits between the tries start at 1 second and double,
    bracketing 1, 2, 4, 8, 16 and 32 seconds from the pinned end's side, and none passes 30."""
    pin_draws(monkeypatch, end)
    final = polled(completed())
    read = read_of(final.body, the_record())
    refusals = [refusal("GET", POLL, "internal-error", 500) for _ in range(6)]
    script = Script([limits_read(), accepted(queued()), *refusals, final, read], clock=clock)

    result = await upload(script, client_class, wait=True)

    waits = clock.waits
    assert len(waits) == 6 and len(script.sent("GET", POLL)) == 7, f"a wait before each of six tries again: {waits}"
    assert bracketed(waits, [1, 2, 4, 8, 16, 32], end), f"each wait brackets its backoff: {waits}"
    assert all(waits[n + 1] == pytest.approx(2 * waits[n]) for n in range(4)), f"the backoff doubles: {waits}"
    assert max(waits) <= 30, f"no wait passes 30 seconds: {waits}"
    assert result.contents == parse_obj_as(Contents, read.body), "the wait goes on to the record"
    assert script.unexpected == [] and script.unanswered == [], (
        f"only the requests the wait calls for: {script.unexpected}"
    )


@CLIENTS
async def test_a_failure_that_lasts_to_the_bound_is_raised_with_the_last_job_seen(
    clock: Clock, client_class: type
) -> None:
    """A poll refused 503 with a wait of 29 seconds on every attempt is tried again while the wait before the next try
    ends within the bound, then raised with the last job seen. Each poll is one attempt and each wait is the server's,
    so the polls run at 0, 29, ... 1247 seconds; the wait after the 44th would end at 1276, past the bound of 1260, so
    no try begins there: 44 polls and 43 waits, every one the server's 29 seconds, and nothing past the bound."""
    refusals = [refusal("GET", POLL, "overloaded", 503, retry_after=29) for _ in range(44)]
    script = Script([limits_read(), accepted(queued()), *refusals], clock=clock)

    with pytest.raises(ServiceUnavailableError) as raised:
        await upload(script, client_class, wait=True)

    assert clock.waits == [29] * 43, f"every wait is the server's 29 seconds, none past the bound: {clock.waits}"
    assert len(script.sent("GET", POLL)) == 44 and clock.now == 1247, (
        "no try begins whose wait would end past the bound"
    )
    assert raised.value.body.request_id == refusals[-1].body["request_id"], "the last refusal is the one raised"
    assert getattr(raised.value, "job", None) == parse_obj_as(Job, queued()), "it carries the last job seen"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


@CLIENTS
async def test_a_4xx_on_a_poll_ends_the_wait_as_it_arrived(client_class: type) -> None:
    """A poll refused with a 4xx ends the wait at once: the typed error of its status is raised with the problem as it
    arrived, and nothing is polled again."""
    refused = refusal("GET", POLL, "not-found", 404)
    script = Script([limits_read(), accepted(queued()), polled(queued()), refused])

    with pytest.raises(NotFoundError) as raised:
        await upload(script, client_class, wait=True)

    assert json.loads(raised.value.body.json()) == refused.body, "the 4xx is raised with its problem as it arrived"
    assert len(script.sent("GET", POLL)) == 2, "a 4xx ends the wait at once"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"
