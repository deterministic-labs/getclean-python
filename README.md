# getclean for Python

The official Python SDK for getclean, the data layer for research agents. It fetches web pages and documents as clean, exact text with the facts of their source, searches the web and specialist sources with a receipt of what ran, and says in every record what happened and in every billed answer what it cost.

## Install

```sh
pip install getclean
```

Python 3.10 or later. The package ships its type information, so editors and type checkers see every call and every answer.

## A key

A key comes from `https://app.getclean.ai`. The client reads it from the environment variable `GETCLEAN_API_KEY` when you give none, or takes it as `api_key`.

```python
from getclean import GetClean

client = GetClean()
```

```python
from getclean import GetClean

client = GetClean(api_key="...")  # the key as app.getclean.ai shows it
```

A program that signs in can pass a function instead of a value. It is called once per call, and its answer, an API key or an access token, goes out on every attempt of that call.

```python
from getclean import GetClean


def current_token() -> str:
    return "..."  # the access token your sign-in returns


client = GetClean(api_key=current_token)
```

A client built with no key raises `ConfigurationError` before any request leaves. Its message says what to do: `api_key is required: pass it to the client or set the environment variable GETCLEAN_API_KEY.`

The host is `https://api.getclean.ai`. To point the client elsewhere, at a test server for example, pass `base_url` or set `GETCLEAN_BASE_URL`.

## The first call

`fetch_contents` reads a page as a record: its text as Markdown, the words you asked it to find, and a summary when you ask for one. Read the answer in the order it comes: what happened, then the text, then the cost.

```python
from getclean import GetClean

client = GetClean()

contents = client.fetch_contents(
    url="https://example.com/q3",
    highlights=["Revenue rose 12%", "what drove the margin"],
    summary=True,
)

print(contents.outcome.kind, contents.outcome.reason)
if contents.outcome.kind == "delivered":
    print(contents.markdown)
    print(contents.summary)
if contents.cost is not None:
    print(contents.cost.actual.amount, contents.cost.actual.currency)
print(contents.id, contents.expires_at)
```

The text of a record is a third party's, as the source wrote it, and it may carry instructions. A program that hands `markdown` to a model should give it as material to read, never as a message to obey. The contract's [page for agents](https://github.com/deterministic-labs/getclean-api/blob/main/docs/agents.md) says how to read an answer and what a refusal means.

A page that could not be fetched is still a record, not an exception. Its `outcome.kind` is `failed`, `refused` or `needs_person`, and `outcome.reason` says why, so the check above is the one your program needs. `cost` is on every billed answer and absent from a free read. The record's `id` names it from now on. It is kept 48 hours after its last call and at most 30 days, `expires_at` says until when, and every later read of it is free.

## Read the record again

A record is read by its id, free, in the shape you need: the map of its sections without text, one section, or only the blocks of one kind. A list that may run over several pages comes back as a pager: iterate it for the items, and read the page's own members on `response`.

```python
from getclean import GetClean

client = GetClean()
contents_id = "cnt_3Fk9abaUhNX7t2eKkgfd3e"

record = client.get_contents(contents_id, max_characters=0)
for section in record.sections or []:
    print(section.id, section.level, section.title)

margin = client.get_section(contents_id, "s2")
print(margin.section.title, margin.markdown)

blocks = client.list_blocks(contents_id, block_kinds=["table"])
for block in blocks:
    print(block.id, block.kind, block.table)
print(blocks.response.fingerprint, blocks.response.notices)
```

A long section is cut into pages. `iter_section` reads them one after another, each page asked with the token of the page before it, until the last.

```python
from getclean import GetClean

client = GetClean()

for page in client.iter_section("cnt_3Fk9abaUhNX7t2eKkgfd3e", "s2", max_characters=5000):
    print(page.markdown)
```

Every method and every parameter is listed in [reference.md](./reference.md).

## Search

`search` runs one question across the web and specialist sources, ranks what it finds, and can fetch the top results as records in the same call. The answer carries the candidates in rank order and a receipt of every source searched.

```python
from getclean import GetClean, Money, SearchContentsOptions

client = GetClean()

search = client.search(
    query="EU AI Act article 50 marking obligations",
    published_within_days=365,
    max_candidates=3,
    contents=SearchContentsOptions(top=1, max_characters=8000),
    max_cost=Money(amount="0.1000", currency="USD"),
)

for candidate in search.candidates:
    print(candidate.relevance_score, candidate.title, candidate.url)
    print(candidate.source_profile.kind, candidate.source_profile.role)
    if candidate.contents is not None:
        if candidate.contents.truncated:
            for section in candidate.contents.sections or []:
                print(section.id, section.title, section.characters)
        else:
            print(candidate.contents.markdown)
for receipt in search.datasources_searched or []:
    print(receipt.id, receipt.outcome.kind)

stored = client.get_search(search.id)
print(stored.response.outcome.kind, len(stored.response.candidates))
```

A fetched candidate carries its text as `markdown` when it fit under `max_characters`. When it did not, `truncated` is true and `sections` is the map of the content instead, one row per section with its size; `get_section` then reads the section you need.

The stored list is read again with `get_search`, free. It comes back as a pager over the same candidates: iterate it for the candidates, or read the page itself on `response`.

## Upload a document

`upload_contents` sends a file from your machine. Give `document` a path, bytes or a readable stream; a string is a path and is read from your machine, so pass bytes when you have the document's bytes. A short document is answered at once with `contents`. A longer one is parsed as a job: with `wait=True` the client follows the job and reads the record for you.

```python
from getclean import GetClean

client = GetClean()

result = client.upload_contents(document="minutes.pdf", wait=True)
if result.contents is not None:
    print(result.contents.outcome.kind, result.contents.cost)
elif result.job is not None:
    print(result.job.id, result.job.state)
```

With `wait=True` the client polls the job up to a minute at a time, within the job bound, then reads the record. A job that failed with no record raises the typed error of its problem's status; a job canceled before any record exists raises `JobCanceled`, which carries the job. A job still running at the bound comes back as it stands, as the second branch above shows.

Without `wait`, follow the job yourself: `get_job` reads it, waiting up to `wait_seconds` until the job is final or the wait ends, and `get_contents` reads the record once `contents_id` is set.

```python
from getclean import GetClean

client = GetClean()

result = client.upload_contents(document="minutes.pdf")
if result.job is not None:
    job = client.get_job(result.job.id, wait_seconds=60)
    print(job.state, job.finished, job.contents_id)
```

An upload is billed in units: one `contents`, one `document_pages` for each page parsed, one `recognized_pages` for each page recognized from its image, and one `model_steps` for each model field that ran. `get_limits` shows the price of each unit.

## Errors

An HTTP refusal is a typed error, one class per status, all in `getclean.errors`: `BadRequestError`, `UnauthorizedError`, `ForbiddenError`, `NotFoundError`, `ConflictError`, `GoneError`, `ContentTooLargeError`, `UnsupportedMediaTypeError`, `UnprocessableEntityError`, `TooManyRequestsError`, `UnavailableForLegalReasonsError`, `InternalServerError`, `BadGatewayError`, `ServiceUnavailableError` and `GatewayTimeoutError`. Each carries the API's answer as `body`, a `Problem`: `type` names what happened, `title` and `detail` say it in words, `who_must_act` says whether you, the account owner or the service must act, `retryable` says whether asking again can help, and `change`, where the fix is in your request, names the field and the move. The error's message begins with the title and the detail, as in `A field is invalid: formats holds a value outside its set.`, and carries the headers, the status and the body after them.

```python
from getclean import ApiError, GetClean
from getclean.errors import ConflictError

client = GetClean()

try:
    contents = client.fetch_contents(url="https://example.com/q3")
except ConflictError as error:
    problem = error.body
    print(problem.type, problem.title, problem.detail)
    print(problem.who_must_act, problem.retryable, problem.change)
except ApiError as error:
    print(error.status_code, error.body)
```

`ApiError` is the base of every typed error, so one `except ApiError` catches every error of the API. `ConfigurationError` and `JobCanceled` are the SDK's own, imported from `getclean`, and are not HTTP errors.

A value of the wrong type is not refused by the client: a text where a boolean is declared is coerced when a request model is built, or sent as given when the method takes the value directly, so your type checker is what catches it, as in TypeScript, where no check runs either.

## Retries, the key and timeouts

The client retries on its own what a retry can help: `429`, `502`, `503`, `504`, and a `409` whose problem type is `idempotency-key-in-flight`, the answer to a call repeated while its first attempt still runs. One call makes at most five attempts in all. Between attempts it waits as the server's `Retry-After` asks when that is 30 seconds or less, else one second, doubling, never past 30. A `Retry-After` past 30 seconds ends the retries, and the answer comes back to you with `retry_after_seconds` on its body, for your program to decide. `max_retries`, on the client or on a call, changes the count.

Every call that may bill carries one idempotency key, the same on every attempt. The client makes one when you give none, so a retry is a replay of the first attempt and never a second charge. When the call fails, the key is on the error as `idempotency_key`. Give your own key when your program retries across processes, and the API answers the first call's result again.

```python
from getclean import GetClean

client = GetClean()
order = "order-7"  # your own id for the piece of work this call belongs to

contents = client.fetch_contents(
    url="https://example.com/q3",
    idempotency_key=f"{order}:fetch-q3",
    request_options={
        "additional_headers": {"traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"},
    },
)
if contents.cost is not None:
    print(contents.cost.replayed)
```

Each attempt runs under a timeout of its own, which bounds each phase of the attempt, connecting, writing, reading and waiting for the pool, not the attempt as a whole: 120 seconds until the client has read your limits, then, for a call that may bill, the API's own bound for that kind of call plus ten seconds, `call_seconds` for a single call and `batch_seconds` for a batch; a free call keeps 120 seconds. A timeout you set, on the client as `timeout` or on a call as `timeout`, always stands. Headers you add through `request_options`, `traceparent` among them, go on the call and on every poll and read made for it.

## Money

Every call that bills states its cost before and after: `cost.ceiling` is the most it could cost, `cost.actual` what it did. `max_cost` caps one call below the key's cap; the key's cap applies when you give none. `get_limits` reads the account's balance, the caps, the price of each unit and the bounds of every parameter, free.

```python
from getclean import GetClean, Money

client = GetClean()

limits = client.get_limits()
print(limits.balance.amount, limits.balance.currency)
print(limits.caps.call_cap.amount)
print(limits.prices["contents"].amount, limits.prices["model_steps"].amount)
print(limits.bounds.contents["max_characters"].max)

contents = client.fetch_contents(
    url="https://example.com/q3",
    max_cost=Money(amount="0.10", currency="USD"),
)
if contents.cost is not None:
    print(contents.cost.actual.amount, contents.cost.ceiling)
```

Four refusals are about money, and each says in `who_must_act` who must act: `credit-exhausted` when the account's credit is spent, `run-budget-exhausted` and `key-budget-exhausted` when a run's or the key's budget is used up, all three answered 403, and `cost-exceeds-cap`, answered 422, when the cap is below the smallest possible charge. A call repeated under the same key and body within 24 hours is answered again from the first result, with `cost.replayed` true and nothing billed twice.

## Async

`AsyncGetClean` has the same methods, awaited. `iter_section` is an async generator, and a pager is iterated with `async for`.

```python
import asyncio

from getclean import AsyncGetClean


async def main() -> None:
    async with AsyncGetClean() as client:
        contents = await client.fetch_contents(url="https://example.com/q3")
        print(contents.outcome.kind)
        async for page in client.iter_section(contents.id, "s2"):
            print(page.section.id)
        jobs = await client.list_jobs(page_size=10)
        async for job in jobs:
            print(job.id, job.state)


asyncio.run(main())
```

A program that refreshes its token passes `async_token`, an async function called once per call.

## Versioning

This is getclean for Python 0.1.0, built against version 1.0.3 of the getclean API contract. The package's version starts at 0.1.0 and moves to 1.0.0 with the service's first release. A minor change of the contract gives it a minor version; a change in this package alone, in its code, its tests or its documents, gives it a patch version. The version in the package's metadata, in the repository's tag `v<version>` and in the changelog entry is always the same number, and a version is never reused. Every change is listed in [CHANGELOG.md](./CHANGELOG.md).

## Links

- Documentation and the API reference: https://docs.getclean.ai
- The API contract: https://github.com/deterministic-labs/getclean-api
- Every method of this SDK: [reference.md](./reference.md)
- Changes: [CHANGELOG.md](./CHANGELOG.md)
- Licence: MIT, [LICENSE](./LICENSE)
- Security: write to security@getclean.ai, never a public issue
