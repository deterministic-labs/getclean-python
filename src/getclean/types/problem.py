# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .money import Money
from .problem_change import ProblemChange
from .problem_who_must_act import ProblemWhoMustAct
from .violation import Violation


class Problem(UniversalBaseModel):
    """
    An answer that is not a result: `application/problem+json`, RFC 9457, one shape for every status. Read `type` to know what happened, `who_must_act` to know who must act, and `change` or `violations` to know what to change. `type`, `title`, `detail`, `instance`, `request_id`, `who_must_act` and `retryable` are always present; `status` on a top-level problem; every other member when it applies. A problem never carries a stack trace, an internal address, a secret, another caller's data or text from a site or a source. A source's or a site's failure is never a problem: it is that item's outcome.
    """

    type: str = pydantic.Field()
    """
    An absolute URI that names the problem and leads to a page about its fix: `https://api.getclean.ai/problems/<name>`, the name being the last segment. Compare on it; it is kept for good. `about:blank` is used on 405, on 406 and on the 404 of a path no operation has, with the status's reason phrase as the title. Every type, with its status, who must act and its title:
    
    | Type | Status | Who acts | Title |
    |---|---|---|---|
    | `invalid-request` | 400 | caller | The request is invalid |
    | `page-token-invalid` | 400 | caller | The page token is invalid |
    | `unauthorized` | 401 | caller | The key is missing or rejected |
    | `insufficient-scope` | 403 | caller for an access token, account owner for an API key | The key lacks a scope this call needs |
    | `policy-limit-exceeded` | 403 | account owner | The key's policy forbids this |
    | `datasource-access-required` | 403 | account owner | The datasource needs a registered login |
    | `credit-exhausted` | 403 | account owner | The credit is exhausted |
    | `run-budget-exhausted` | 403 | account owner | The run's budget is exhausted |
    | `key-budget-exhausted` | 403 | account owner | The key's budget is exhausted |
    | `not-found` | 404 | caller | Not found |
    | `idempotency-key-in-flight` | 409 | caller, after the wait | The same request is still running |
    | `record-without-content` | 409 | caller | The record has no content |
    | `contents-expired` | 410 | caller | The record has expired |
    | `search-expired` | 410 | caller | The search has expired |
    | `job-expired` | 410 | caller | The job has expired |
    | `body-too-large` | 413 | caller | The body is too large |
    | `unsupported-media-type` | 415 | caller | The media type is not supported |
    | `invalid-field` | 422 | caller | A field is invalid |
    | `destination-refused` | 422 | caller | The destination is refused |
    | `model-work-refused` | 422 | caller | Model work is refused by the request |
    | `cost-exceeds-cap` | 422 | caller | The cost cap is below the smallest call |
    | `version-withdrawn` | 422 | caller | The version is no longer served |
    | `records-incomparable` | 422 | caller | The records cannot be compared |
    | `idempotency-key-reused` | 422 | caller | The idempotency key was reused with another body |
    | `no-datasource-can-run` | 422 | caller | No datasource can run this search |
    | `datasource-unknown` | 422 | caller | The datasource is unknown |
    | `datasource-not-searchable` | 422 | caller | The datasource has no search |
    | `domain-set-unknown` | 422 | caller | The domain set is unknown |
    | `rate-limit-exceeded` | 429 | caller, after the wait | The rate limit is exceeded |
    | `concurrency-limit-exceeded` | 429 | caller, after the wait | Too many calls are in flight |
    | `legal-block` | 451 | caller | Withheld under a legal demand |
    | `about:blank` | 405, 406, the 404 of a path no operation has | caller | the status's reason phrase |
    | `internal-error` | 500 | service | The service failed |
    | `gateway-error` | 502 | service | A step behind the service failed |
    | `overloaded` | 503 | service | The service is overloaded |
    | `gateway-timeout` | 504 | service | A step behind the service timed out |
    """

    title: str = pydantic.Field()
    """
    The type's published title, as the table under `type` gives it.
    """

    status: typing.Optional[int] = pydantic.Field(default=None)
    """
    The HTTP status. Present on a top-level problem; absent on a problem nested in a batch result or a job, where it could not equal the response's status.
    """

    detail: str = pydantic.Field()
    """
    One sentence that names what went wrong, written for a person to read. Always present. A credential is never echoed.
    """

    instance: str = pydantic.Field()
    """
    The URI of this one occurrence: `https://api.getclean.ai/requests/<request_id>`, with `/items/<index>` appended for a problem nested in a batch result. Unique per occurrence. It is an identifier and is not served as a page.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header. A nested problem carries the call's id too.
    """

    who_must_act: ProblemWhoMustAct = pydantic.Field()
    """
    Who must act: `caller`, you; `account_owner`, the person who holds the account; `service`, getclean. A closed set. A site's or a source's failure is never a problem, so no value names them.
    """

    retryable: bool = pydantic.Field()
    """
    True on the six types a retry can help: `idempotency-key-in-flight`, `rate-limit-exceeded`, `concurrency-limit-exceeded`, `overloaded`, `gateway-error` and `gateway-timeout`. False on every other type.
    """

    retry_after_seconds: typing.Optional[int] = pydantic.Field(default=None)
    """
    Seconds to wait before asking again, equal to the `Retry-After` header. Present when known.
    """

    change: typing.Optional[ProblemChange] = pydantic.Field(default=None)
    """
    The fix as data: the field to change, the values or range it may take, or the operation to call instead. Present when a fix is data.
    """

    violations: typing.Optional[typing.List[Violation]] = pydantic.Field(default=None)
    """
    Every fault of the request at once, each with where it is. Present on `invalid-field`, `model-work-refused` and `invalid-request`.
    """

    balance: typing.Optional[Money] = pydantic.Field(default=None)
    """
    The prepaid credit left. Present on `credit-exhausted`.
    """

    amount_needed: typing.Optional[Money] = pydantic.Field(default=None)
    """
    What the limit that binds lacks for the smallest call: the call's price less what the limit holds. A balance of 0.0020 against a call of 0.0050 gives 0.0030. Present on `credit-exhausted`, `run-budget-exhausted` and `key-budget-exhausted`.
    """

    funding_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The account owner's page for that balance or budget at `https://app.getclean.ai`. Present on `credit-exhausted`, `run-budget-exhausted` and `key-budget-exhausted`.
    """

    minimum_cap: typing.Optional[Money] = pydantic.Field(default=None)
    """
    The smallest call's price, the least cap that would run it. Present on `cost-exceeds-cap`, and on `policy-limit-exceeded` when the key's cap is the limit.
    """

    run_budget_remaining: typing.Optional[Money] = pydantic.Field(default=None)
    """
    What is left of the run's budget. Present on `run-budget-exhausted`.
    """

    key_budget_remaining: typing.Optional[Money] = pydantic.Field(default=None)
    """
    What is left of the key's budget. Present on `key-budget-exhausted`.
    """

    demand: typing.Optional[str] = pydantic.Field(default=None)
    """
    The legal demand made on getclean. Present on `legal-block`.
    """

    demanded_by: typing.Optional[str] = pydantic.Field(default=None)
    """
    Who made the demand. Present on `legal-block`.
    """

    applies_to: typing.Optional[str] = pydantic.Field(default=None)
    """
    What the demand covers. Present on `legal-block`.
    """

    expired_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    When the record or the job expired, RFC 3339 in UTC. Present on `contents-expired`, `search-expired` and `job-expired`.
    """

    scopes_required: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Every scope the call needs, among `contents:fetch`, `contents:read`, `contents:model`, `contents:delete`, `jobs:read`, `jobs:cancel`, `limits:read`, `search:run` and `search:read`, an open set. Present on `insufficient-scope`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
