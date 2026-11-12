"""The host and the credential: the host from GETCLEAN_BASE_URL when no base_url is given; a client with no credential,
or an empty one, refused at construction; a credential function called once per call, the retries of that call reusing
what it returned, a later page or poll being a call of its own; async_token a credential on its own."""

import typing

import httpx
import pytest
from ._support import (
    CLIENTS,
    DOCUMENT,
    FETCH,
    Answer,
    Body,
    Script,
    accepted,
    clock,
    completed,
    example,
    items_of,
    limits_read,
    polled,
    queued,
    read_of,
    request_id,
    settle,
    the_record,
    under_request_id,
)

from getclean import ApiError, ConfigurationError

# Every test of this file runs with time stood in, so that none waits for real, even on a client that waits
# where it should not.
pytestmark = pytest.mark.usefixtures(clock.__name__)

API_HOST = "https://api.getclean.ai"
"""The API's host, the contract's server."""


class Tokens:
    """A credential function that returns a new token at each call and counts its calls."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self) -> str:
        self.calls += 1
        return f"token-{self.calls}"


def bearers(requests: typing.Sequence[httpx.Request]) -> typing.List[str]:
    return [request.headers.get("Authorization", "") for request in requests]


@CLIENTS
async def test_the_host_comes_from_the_variable_when_no_base_url_is_given(
    monkeypatch: pytest.MonkeyPatch, client_class: type
) -> None:
    """With no base_url, GETCLEAN_BASE_URL, set and not empty, is the host."""
    monkeypatch.setenv("GETCLEAN_BASE_URL", "http://environment.test")
    script = Script([limits_read()])

    await settle(script.client_for(client_class, base_url=None).get_limits())

    assert str(script.requests[0].url) == "http://environment.test/v1/limits", "the host from GETCLEAN_BASE_URL"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
async def test_a_base_url_argument_wins_over_the_variable(monkeypatch: pytest.MonkeyPatch, client_class: type) -> None:
    """A base_url given to the client is the host even when GETCLEAN_BASE_URL is set."""
    monkeypatch.setenv("GETCLEAN_BASE_URL", "http://environment.test")
    script = Script([limits_read()])

    await settle(script.client_for(client_class, base_url="http://argument.test").get_limits())

    assert str(script.requests[0].url) == "http://argument.test/v1/limits", "the base_url given wins"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("variable", [None, ""], ids=["unset", "empty"])
async def test_with_no_base_url_and_no_variable_the_host_is_the_apis(
    monkeypatch: pytest.MonkeyPatch, client_class: type, variable: typing.Optional[str]
) -> None:
    """With no base_url, an unset or empty GETCLEAN_BASE_URL leaves the API's own host, an empty value being none."""
    if variable is None:
        monkeypatch.delenv("GETCLEAN_BASE_URL", raising=False)
    else:
        monkeypatch.setenv("GETCLEAN_BASE_URL", variable)
    script = Script([limits_read()])

    await settle(script.client_for(client_class, base_url=None).get_limits())

    assert str(script.requests[0].url) == f"{API_HOST}/v1/limits", "the API's own host"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


@CLIENTS
def test_no_credential_raises_the_configuration_error_at_construction(
    monkeypatch: pytest.MonkeyPatch, client_class: type
) -> None:
    """A client built with neither api_key nor GETCLEAN_API_KEY raises ConfigurationError at construction, the SDK's own
    error and never an HTTP one, its message naming both ways to give the key; no request leaves."""
    monkeypatch.delenv("GETCLEAN_API_KEY", raising=False)
    script = Script([])

    with pytest.raises(ConfigurationError) as raised:
        script.client_for(client_class, api_key=None)

    assert not isinstance(raised.value, ApiError), "the SDK's own error, never an HTTP error class"
    assert "api_key" in str(raised.value) and "GETCLEAN_API_KEY" in str(raised.value), (
        "the message names the argument to pass and the variable to set"
    )
    assert script.requests == [], "no request leaves"


@CLIENTS
@pytest.mark.parametrize("given", ["an empty api_key", "an empty variable"])
def test_an_empty_credential_is_no_credential(monkeypatch: pytest.MonkeyPatch, client_class: type, given: str) -> None:
    """An empty api_key, or an empty GETCLEAN_API_KEY with no api_key, is no credential: the same ConfigurationError at
    construction, so no empty bearer value leaves."""
    if given == "an empty api_key":
        monkeypatch.delenv("GETCLEAN_API_KEY", raising=False)
        api_key: typing.Optional[str] = ""
    else:
        monkeypatch.setenv("GETCLEAN_API_KEY", "")
        api_key = None
    script = Script([])

    with pytest.raises(ConfigurationError):
        script.client_for(client_class, api_key=api_key)

    assert script.requests == [], "no request leaves"


RETRIED = {
    # A first attempt answered with something a retry can help, asking a wait of 1 second.
    "a 503": ("overloaded", 503),
    "an in-flight 409": ("idempotency-key-in-flight", 409),
}


@CLIENTS
@pytest.mark.parametrize("first", RETRIED.values(), ids=RETRIED.keys())
async def test_the_credential_function_runs_once_for_a_call_and_its_retry(
    client_class: type, first: typing.Tuple[str, int]
) -> None:
    """A credential function runs once per call, before its first attempt, and the retry of that call, after a 503 or an
    in-flight 409 alike, reuses what it returned. The limits read before the fetch is a call of its own, and runs it
    once more."""
    tokens = Tokens()
    script = Script([limits_read(), FETCH.refused(*first, retry_after=1), FETCH.answered()])

    await settle(FETCH.on(script.client_for(client_class, api_key=tokens)))

    assert bearers(script.requests) == ["Bearer token-1", "Bearer token-2", "Bearer token-2"], (
        "one token for the limits read, one for the fetch, reused on its retry"
    )
    assert tokens.calls == 2, "the function runs once for the limits read and once for the fetch"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"


def jobs_page(job_id: str, next_page_token: typing.Optional[str]) -> Body:
    """list_jobs' example under a request id of its own, its one job under this id, with the token of the page after it,
    an opaque string, or none on the last."""
    body = under_request_id(example("list_jobs.first-page"), request_id())
    body["jobs"][0]["id"] = job_id
    if next_page_token is not None:
        body["next_page_token"] = next_page_token
    return body


@CLIENTS
async def test_each_page_of_a_pager_is_a_new_call_that_runs_the_function_again(client_class: type) -> None:
    """A later page of a pager is a new call, which runs the credential function again."""
    tokens = Tokens()
    script = Script(
        [
            Answer("GET", "/v1/jobs", 200, jobs_page("job_" + "first".ljust(22, "x"), "t2")),
            Answer("GET", "/v1/jobs", 200, jobs_page("job_" + "second".ljust(22, "x"), None)),
        ]
    )

    await items_of(await settle(script.client_for(client_class, api_key=tokens).list_jobs()))

    assert bearers(script.requests) == ["Bearer token-1", "Bearer token-2"], "a token for each page"
    assert script.unexpected == [], f"only the requests the pager calls for: {script.unexpected}"


@CLIENTS
async def test_each_poll_of_the_wait_runs_the_function_again(client_class: type) -> None:
    """Each poll of the upload's wait, and the record's read after it, is a call of its own that runs the credential
    function again, so a caller that refreshes hands every poll a live token."""
    tokens = Tokens()
    final = polled(completed())
    script = Script([limits_read(), accepted(queued()), polled(queued()), final, read_of(final.body, the_record())])

    await settle(script.client_for(client_class, api_key=tokens).upload_contents(document=DOCUMENT, wait=True))

    assert bearers(script.requests) == [f"Bearer token-{n}" for n in range(1, 6)], "a token for each call"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


async def test_async_token_alone_is_a_credential(monkeypatch: pytest.MonkeyPatch) -> None:
    """AsyncGetClean built with async_token alone, no api_key and no GETCLEAN_API_KEY, is accepted, and its calls carry
    the token the function returns."""
    monkeypatch.delenv("GETCLEAN_API_KEY", raising=False)

    async def token() -> str:
        return "async-token"

    script = Script([limits_read()])

    await script.async_client(api_key=None, async_token=token).get_limits()

    assert bearers(script.requests) == ["Bearer async-token"], "the call carries the async function's token"
    assert script.unexpected == [], f"only the requests the call calls for: {script.unexpected}"
