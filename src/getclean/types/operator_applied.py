# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .operator_state import OperatorState


class OperatorApplied(UniversalBaseModel):
    """
    How one operator was applied on one source.
    """

    state: OperatorState = pydantic.Field()
    """
    How it was applied: `native`, `emulated`, `dropped` or `not_applicable`, as `OperatorState` defines them.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
