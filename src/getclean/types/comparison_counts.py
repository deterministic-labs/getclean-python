# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class ComparisonCounts(UniversalBaseModel):
    """
    The tally of a comparison, by kind of change.
    """

    added: int = pydantic.Field()
    """
    Blocks only on the current side.
    """

    removed: int = pydantic.Field()
    """
    Blocks only on the baseline side.
    """

    changed: int = pydantic.Field()
    """
    Blocks paired above the published similarity whose text differs.
    """

    moved: int = pydantic.Field()
    """
    Blocks with the same text at another position in the block order.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
