# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .cost import Cost
from .job_counts import JobCounts
from .outcome import Outcome
from .problem import Problem


class Job(UniversalBaseModel):
    """
    A parse that outlives its request. `completed` when its record is delivered or partial, `failed` otherwise, with `problem` set when nothing was made; `canceled` keeps and bills the pages done. Kept 30 days after its end, then `410 job-expired` for 30 days, then `404`. A job carries no notices and no version.
    """

    id: str = pydantic.Field()
    """
    The job's id, `job_` and 22 random characters; another account's id answers `404`.
    """

    kind: str = pydantic.Field()
    """
    The operation that started the job, `upload_contents`; an open set.
    """

    state: str = pydantic.Field()
    """
    The job's state: `queued`, `running`, `completed`, `failed` or `canceled`; the last three are final. An open set.
    """

    finished: bool = pydantic.Field()
    """
    True once the state is final.
    """

    stage: typing.Optional[str] = pydantic.Field(default=None)
    """
    What the job is doing now, `parsing` or `recognizing`; an open set. Absent on `queued` and when final.
    """

    counts: JobCounts = pydantic.Field()
    """
    The pages parsed, failed and remaining, adding up to `pages.count`; zeros while the job is queued or the count unread.
    """

    cost: Cost = pydantic.Field()
    """
    The units so far on every read, the final figure once `finished`; zero on a cancel with no page done.
    """

    outcome: typing.Optional[Outcome] = pydantic.Field(default=None)
    """
    The record's outcome. Present once a record exists.
    """

    retry_after_seconds: typing.Optional[int] = pydantic.Field(default=None)
    """
    Seconds to wait before reading again, equal to the `Retry-After` header of `get_job` and `cancel_job`; inside a `JobPage`, each job's own wait. Absent once final.
    """

    contents_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The record the job made, read by `get_contents`. Present once a record exists.
    """

    problem: typing.Optional[Problem] = pydantic.Field(default=None)
    """
    Why the job failed before a record existed, without `status`, its `request_id` and `instance` the upload's. Present only on a job that failed with no record.
    """

    created_at: dt.datetime = pydantic.Field()
    """
    When the job started, RFC 3339 in UTC.
    """

    updated_at: dt.datetime = pydantic.Field()
    """
    When the job last changed, RFC 3339 in UTC.
    """

    expires_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    When the job expires, 30 days after it ended, RFC 3339 in UTC. Absent until final.
    """

    request_id: str = pydantic.Field()
    """
    The id of the call this copy of the job came back in, the same as that call's `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
