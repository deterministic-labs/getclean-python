# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .problem import Problem
from .search import Search


class SearchBatchResult(UniversalBaseModel):
    """
    One item's result: its search record, or the problem that skipped it, exactly one of the two present.
    """

    index: int = pydantic.Field()
    """
    The item's position in the request, from 0.
    """

    label: typing.Optional[str] = pydantic.Field(default=None)
    """
    Your label for the item, as sent. Present when given.
    """

    search: typing.Optional[Search] = pydantic.Field(default=None)
    """
    The search record, with the batch call's `request_id`, its `applied_request` the item's fields merged with the top's, and its own `expires_at`. Present when the item ran.
    """

    problem: typing.Optional[Problem] = pydantic.Field(default=None)
    """
    Why the item was skipped, without `status`, its `instance` ending in `/items/<index>`. Present when the item was skipped.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
