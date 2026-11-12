# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class CellConfidence(UniversalBaseModel):
    """
    How sure the recognition was of one cell of a table read from a scan.
    """

    row: int = pydantic.Field()
    """
    The cell's row, from 0.
    """

    column: int = pydantic.Field()
    """
    The cell's column, from 0.
    """

    confidence: float = pydantic.Field()
    """
    The confidence, 0 to 1.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
