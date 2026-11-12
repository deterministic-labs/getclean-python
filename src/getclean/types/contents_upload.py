# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .contents import Contents
from .job import Job


class ContentsUpload(UniversalBaseModel):
    """
    What `upload_contents` answers. On a `201` it carries `contents`, the record, since the parse finished within `wait_seconds`; on a `202` it carries `job`, since the parse goes on. Exactly one of the two is present on the wire; both are optional in this schema because one schema serves both answers. On a `202`, read the job with `get_job` until it is final, then read the record with `get_contents`.
    """

    contents: typing.Optional[Contents] = pydantic.Field(default=None)
    """
    The record, with the members its outcome carries and its `cost`. Present on a `201`.
    """

    job: typing.Optional[Job] = pydantic.Field(default=None)
    """
    The job, stored before this answer is sent, so a read of it never misses. Present on a `202`.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
