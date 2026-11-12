# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .filter_state import FilterState


class FilterApplied(UniversalBaseModel):
    """
    How one hard filter was applied on one source.
    """

    state: FilterState = pydantic.Field()
    """
    How it was applied: `native`, `emulated`, `skipped` or `not_applicable`, as `FilterState` defines them.
    """

    how: typing.Optional[str] = pydantic.Field(default=None)
    """
    How getclean emulated it. Present on `emulated`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
