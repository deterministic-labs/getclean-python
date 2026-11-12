"""What a developer reads in help() and in the editor. The methods the client writes again open with the operation's own
description, whole, then a paragraph of the client's own, which states each rule the client adds to that method, then
the generated parameter and return sections, `wait` documented among the upload's parameters; the two client classes
carry a docstring of their own that states the credential, the host, the one count of retries and the timeout of each
attempt; with_raw_response says what the raw client returns. Each fact is checked by a phrase that carries its sense, so
a sentence that names the same things in the opposite sense does not pass."""

import inspect
import re
import typing

import pytest
from ._support import CLIENTS

from getclean import AsyncGetClean, GetClean
from getclean.base_client import AsyncBaseGetClean, BaseGetClean

BASE = {GetClean: BaseGetClean, AsyncGetClean: AsyncBaseGetClean}

FIRST_SENTENCES = {
    # The first sentence of each operation's description in the API's contract.
    "upload_contents": "Read a document you hold, or one at a URL that needs more time than a fetch gives.",
    "list_jobs": "List the account's jobs, newest first, free.",
    "list_contents": "List the records the account keeps, newest first, free.",
}

Fact = typing.Tuple[str, str]
"""A fact and the pattern of a phrase that states it in its own sense."""

UPLOAD_FACTS: typing.List[Fact] = [
    # Each rule the client adds to upload_contents.
    ("the wait is off by default", r"`?wait`? is off by default"),
    ("an upload answered 201 comes back as answered", r"\b201\b[^.;]*\bcomes back as answered\b"),
    ("a 201 brings the record with its cost", r"`?contents`? with its `?cost`? on a 201\b"),
    (
        "document takes a path, bytes or a readable stream",
        r"takes the path of a file\b[^;]*\bbytes, or a readable stream\b",
    ),
    (
        "a path, a str or an os.PathLike, means the file at that path",
        r"`?str`? or `?os\.PathLike`?: the file at that path\b",
    ),
    (
        "a stream is read into memory once, before the first attempt",
        r"\bread into memory once before the first attempt\b",
    ),
    (
        "a path that names no file raises FileNotFoundError before any request",
        r"\bnames no file raises\b[^.;]*\bFileNotFoundError before any request\b",
    ),
    ("wait=True follows a 202's job to its end", r"`?wait=True`? the call follows a 202's job to its end\b"),
    ("the job is polled up to a minute at a time", r"\bpolled up to a minute at a time\b"),
    ("each poll runs under a timeout of its own", r"\beach poll under a timeout of its own\b"),
    ("each poll carries the caller's headers", r"\beach poll\b[^.;]*\bcarrying your headers\b"),
    (
        "the read carries the caller's headers",
        r"\b(the record is read|the read)\b[^.;]*\b(carrying|carries|with) your headers\b",
    ),
    (
        "the polls and the read carry none of the upload's query, body or timeout options",
        r"\bnone of the upload's\b[^.;]*\b(query|body)\b",
    ),
    (
        "the polls go on until the job is final or the job bound and one more minute have passed",
        r"\buntil it is final or the job bound and one more minute have passed\b",
    ),
    (
        "the job bound is the limits' contents job_seconds, 30 minutes until they are read",
        r"\bthe bound being the limits' contents `?job_seconds`?, 30 minutes until the limits are read\b",
    ),
    (
        "the record is read under the upload's own max_characters",
        r"\brecord is read under this call's `?max_characters`?",
    ),
    (
        "the read takes only the lists the upload sent among formats and block_kinds",
        r"\bthe lists it sent among `?formats`? and `?block_kinds`?",
    ),
    (
        "ContentsUpload comes back with the record and the final job",
        r"\bContentsUpload comes back with `?contents`? and the final `?job`?",
    ),
    ("the final job's cost is the bill", r"\bthe final `?job`?, whose `?cost`? is the bill\b"),
    (
        "a poll or the read failing with a 429, a 5xx or no answer is tried again within the bound",
        r"\b429, a 5xx or no answer is tried again within the bound\b",
    ),
    (
        "a poll or the read is tried again after the server's wait or a backoff",
        r"\btried again\b[^.;]*\bafter the server's wait or a backoff\b",
    ),
    ("a 4xx ends the wait with that error", r"\ba 4xx ends the call with that error\b"),
    (
        "a job failed with no record raises the error class of its problem's status",
        r"\bfailed with no record raises the error class of its problem's status\b",
    ),
    ("a job canceled with no record raises JobCanceled", r"\bcanceled with no record raises JobCanceled\b"),
    (
        "every error the wait raises carries the last job seen as job",
        r"\bevery error the wait raises carries the last job seen as `?job`?",
    ),
    (
        "every error the wait raises carries the upload's key as idempotency_key",
        r"\bthe key the upload sent as `?idempotency_key`?",
    ),
]

REPEAT_FACTS: typing.List[Fact] = [
    # The rule the client adds to the two lists that grow while they page.
    ("the list grows while it pages", r"\bthe list grows while it pages\b"),
    (
        "an item whose id was already seen is dropped, page after page",
        r"\bdrops an item whose `?id`? was already seen, page after page\b",
    ),
]

RAW_FACTS: typing.List[Fact] = [
    # What the docstring of with_raw_response states of the raw client.
    ("the raw client carries none of this client's additions", r"\bnone of this client's additions\b"),
    (
        "a list operation returns the pager itself, its page carrying request_id",
        r"\ba list operation returns the pager itself, whose `?response`? is the page with its `?request_id`?",
    ),
    ("the headers of a page are not carried", r"\bthe headers of a page are not carried\b"),
]

CLASS_FACTS: typing.List[Fact] = [
    # What the class docstring states of the client as a whole.
    (
        "the credential is api_key, an API key or an access token",
        r"\bcredential is `?api_key`?: an API key or an access token\b",
    ),
    ("the credential may be a function that returns one", r"\bor as a function that returns one\b"),
    (
        "with no api_key the credential is GETCLEAN_API_KEY",
        r"\bwhen none is given, the environment variable GETCLEAN_API_KEY\b",
    ),
    (
        "a client built with no credential raises ConfigurationError before any request leaves",
        r"\bbuilt with neither raises ConfigurationError before any request leaves\b",
    ),
    (
        "the host is the API's, base_url or GETCLEAN_BASE_URL",
        r"\bhost is https://api\.getclean\.ai, or `?base_url`?, or the environment variable GETCLEAN_BASE_URL\b",
    ),
    ("the client retries 429, 502, 503 and 504", r"\bthe client retries 429, 502, 503, 504\b"),
    (
        "the client retries a 409 whose problem type is idempotency-key-in-flight",
        r"\band a 409 whose problem type is idempotency-key-in-flight\b",
    ),
    (
        "one count of five attempts in all, which max_retries changes",
        r"\bfive attempts in all\b[^.;]*\b`?max_retries`? changing the count\b",
    ),
    (
        "the timeout of an attempt bounds each of its phases and is the operation's own bound plus ten seconds",
        r"\bthe timeout of an attempt, which bounds each of its phases, connecting, writing, reading and waiting"
        r"\s+for the\s+pool, is the operation's own bound from the limits plus ten seconds\b",
    ),
    (
        "the timeout of an attempt is 120 seconds for a free call and until the limits are read",
        r"\b120 seconds for a free\s+call and until the limits are read\b",
    ),
    ("a timeout set on the call or on the client stands", r"\ba timeout you set on the call or on the client stands\b"),
]

ASYNC_TOKEN = r"\bor `?async_token`?, an async function\b"
"""The phrase by which AsyncGetClean's docstring names async_token a credential of its own."""


def flat(text: str) -> str:
    """The text with its line breaks and runs of spaces read as one space, as a reader reads it."""
    return " ".join(text.split())


def states(text: str, pattern: str) -> bool:
    """Whether the text carries the phrase, read as a reader reads it, whatever its capitals."""
    return re.search(pattern, flat(text), re.IGNORECASE) is not None


SECTIONS = r"\n\n(?:Parameters|Returns|Raises|Yields|Examples)\n-+\n"
"""Where a numpydoc docstring's sections begin, after its description."""


def description_of(method: typing.Any) -> str:
    """The description of a method's docstring: what stands before its first section."""
    return re.split(SECTIONS, inspect.cleandoc(method.__doc__ or ""), maxsplit=1)[0]


def paragraph_of(client_class: type, method: str) -> str:
    """What the client's method adds after the operation's own description and before the sections; nothing when the
    docstring does not open with that description, since a fact stated anywhere else is not where a reader looks for
    it."""
    description = description_of(getattr(BASE[client_class], method))
    doc = inspect.cleandoc(getattr(client_class, method).__doc__ or "")
    if not (description and doc.startswith(description)):
        return ""
    return flat(re.split(SECTIONS, doc[len(description) :], maxsplit=1)[0])


@CLIENTS
@pytest.mark.parametrize("method", list(FIRST_SENTENCES))
def test_a_rewritten_method_opens_with_the_operations_description_then_the_clients_paragraph(
    client_class: type, method: str
) -> None:
    """upload_contents, list_jobs and list_contents, which the client writes again, open with the operation's own
    description, whole, as the base client carries it from the contract; a paragraph of the client's own follows it, and
    the generated parameter and return sections follow that, the upload's listing `wait` before request_options: the
    contract says what the API does, and the client's own docs say what the client adds."""
    doc = inspect.cleandoc(getattr(client_class, method).__doc__ or "")
    description = description_of(getattr(BASE[client_class], method))

    assert doc.startswith(FIRST_SENTENCES[method]), f"the contract's first sentence comes first: {doc[:120]!r}"
    assert description and doc.startswith(description), "the operation's whole description comes first, unchanged"
    own = doc[len(description) :]
    assert own.startswith("\n\n") and own.strip(), "a paragraph of the client's own follows the description"
    assert "\n\nParameters\n----------\n" in own, "the generated parameter section follows the paragraph"
    if method == "upload_contents":
        parameters = own.split("\n\nParameters\n----------\n", 1)[1].split("\n\nReturns\n", 1)[0]
        assert "wait : bool" in parameters, "wait is documented among the parameters"
        assert parameters.index("wait : bool") < parameters.index("request_options :"), (
            "wait is listed before request_options"
        )


@CLIENTS
@pytest.mark.parametrize("fact, phrase", UPLOAD_FACTS, ids=[fact for fact, _ in UPLOAD_FACTS])
def test_the_uploads_paragraph_states_each_rule_of_the_wait(client_class: type, fact: str, phrase: str) -> None:
    """The paragraph upload_contents adds states each rule the client adds to the upload, each in its own sense: the
    forms of document, the wait, the polls, the read, what comes back, what is tried again and what each ending
    raises."""
    paragraph = paragraph_of(client_class, "upload_contents")

    assert states(paragraph, phrase), f"the upload's paragraph states that {fact}: {paragraph!r}"


@CLIENTS
@pytest.mark.parametrize("method", ["list_jobs", "list_contents"])
@pytest.mark.parametrize("fact, phrase", REPEAT_FACTS, ids=[fact for fact, _ in REPEAT_FACTS])
def test_the_paragraph_of_a_growing_list_states_the_repeat_filter(
    client_class: type, method: str, fact: str, phrase: str
) -> None:
    """The paragraph list_jobs and list_contents add states that the list grows while it pages and that an item already
    seen is dropped by its id."""
    paragraph = paragraph_of(client_class, method)

    assert states(paragraph, phrase), f"the paragraph of {method} states that {fact}: {paragraph!r}"


@CLIENTS
@pytest.mark.parametrize("fact, phrase", CLASS_FACTS, ids=[fact for fact, _ in CLASS_FACTS])
def test_a_client_class_states_the_credential_the_host_the_retries_and_the_timeout(
    client_class: type, fact: str, phrase: str
) -> None:
    """GetClean and AsyncGetClean carry a docstring of their own, not the base client's, which states the credential,
    the host, the one count of retries and the timeout of each attempt, each in its own sense."""
    doc = client_class.__dict__.get("__doc__") or ""

    assert doc and flat(doc) != flat(BASE[client_class].__doc__ or ""), "the class carries a docstring of its own"
    assert states(doc, phrase), f"{client_class.__name__}'s docstring states that {fact}"


def test_the_async_clients_docstring_names_async_token_a_credential_of_its_own() -> None:
    """AsyncGetClean takes async_token, an async function, as a credential on its own, and its docstring says so."""
    doc = AsyncGetClean.__dict__.get("__doc__") or ""

    assert states(doc, ASYNC_TOKEN), "AsyncGetClean's docstring names async_token, an async function, as a credential"


@CLIENTS
@pytest.mark.parametrize("fact, phrase", RAW_FACTS, ids=[fact for fact, _ in RAW_FACTS])
def test_with_raw_response_states_what_the_raw_client_returns(client_class: type, fact: str, phrase: str) -> None:
    """with_raw_response carries a docstring of its own, which states that the raw client has none of this client's
    additions and that a list operation returns the pager itself, whose page carries its request_id and not its
    headers."""
    doc = getattr(client_class, "with_raw_response").__doc__ or ""

    assert states(doc, phrase), f"with_raw_response's docstring states that {fact}: {flat(doc)!r}"
