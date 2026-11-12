# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .contents import Contents
from .problem import Problem


class ContentsBatchResult(UniversalBaseModel):
    """
    One item's result: its record, or the problem that skipped it; exactly one of the two is present.
    """

    index: int = pydantic.Field()
    """
    The item's position in the request, from 0.
    """

    label: typing.Optional[str] = pydantic.Field(default=None)
    """
    Your label for the item, as sent. Present when given.
    """

    contents: typing.Optional[Contents] = pydantic.Field(default=None)
    """
    The record, with the members its outcome carries and its own `cost`. Present when the item was fetched.
    """

    problem: typing.Optional[Problem] = pydantic.Field(default=None)
    """
    Why the item was skipped, without `status`, its `instance` ending in `/items/<index>`. Present when the item was skipped.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
