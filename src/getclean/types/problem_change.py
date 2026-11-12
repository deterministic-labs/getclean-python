# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .bound import Bound


class ProblemChange(UniversalBaseModel):
    """
    The fix as data. Each member is present when it applies.
    """

    field: typing.Optional[str] = pydantic.Field(default=None)
    """
    The field to change: a field of the operation `operation` names when it is present, else of this request.
    """

    allowed_values: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    The values the field may take.
    """

    bounds: typing.Optional[Bound] = pydantic.Field(default=None)
    """
    The range the field may take.
    """

    operation: typing.Optional[str] = pydantic.Field(default=None)
    """
    The operation to call instead, by its id, one of this contract's 22 operation ids: `fetch_contents`, `list_contents`, `get_contents`, `delete_contents`, `get_section`, `list_blocks`, `list_links`, `upload_contents`, `list_jobs`, `get_job`, `cancel_job`, `fetch_contents_batch`, `highlight_contents`, `fill_schema`, `summarize_contents`, `compare_contents`, `get_limits`, `search`, `get_search`, `search_batch`, `list_datasources`, `get_datasource`; an open set.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
