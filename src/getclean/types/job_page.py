# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .job import Job
from .notice import Notice


class JobPage(UniversalBaseModel):
    """
    One page of the account's jobs, the answer of `list_jobs`, newest first.
    """

    jobs: typing.List[Job] = pydantic.Field()
    """
    The jobs of this page; `[]` when none matches.
    """

    next_page_token: typing.Optional[str] = pydantic.Field(default=None)
    """
    The token for the next page; pass it as `page_token`. Present while more remains, and a page that carries it always has at least one job.
    """

    notices: typing.List[Notice] = pydantic.Field()
    """
    This call's notices, `page_size_lowered`; `[]` when there is none.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
