# Derived from the getclean API contract's problem types when the SDK is built; do not edit.
"""The status of every named problem type of the contract, read from the table in Problem.type.

A problem nested in a job carries no status; the client raises it as the error class of the status its type
names here (client.py, the upload's wait helper).
"""

import typing

PROBLEM_STATUS_BY_TYPE: typing.Dict[str, int] = {
    "body-too-large": 413,
    "concurrency-limit-exceeded": 429,
    "contents-expired": 410,
    "cost-exceeds-cap": 422,
    "credit-exhausted": 403,
    "datasource-access-required": 403,
    "datasource-not-searchable": 422,
    "datasource-unknown": 422,
    "destination-refused": 422,
    "domain-set-unknown": 422,
    "gateway-error": 502,
    "gateway-timeout": 504,
    "idempotency-key-in-flight": 409,
    "idempotency-key-reused": 422,
    "insufficient-scope": 403,
    "internal-error": 500,
    "invalid-field": 422,
    "invalid-request": 400,
    "job-expired": 410,
    "key-budget-exhausted": 403,
    "legal-block": 451,
    "model-work-refused": 422,
    "no-datasource-can-run": 422,
    "not-found": 404,
    "overloaded": 503,
    "page-token-invalid": 400,
    "policy-limit-exceeded": 403,
    "rate-limit-exceeded": 429,
    "record-without-content": 409,
    "records-incomparable": 422,
    "run-budget-exhausted": 403,
    "search-expired": 410,
    "unauthorized": 401,
    "unsupported-media-type": 415,
    "version-withdrawn": 422,
}
