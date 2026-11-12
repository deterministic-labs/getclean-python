# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class CellAddress(UniversalBaseModel):
    """
    One cell of a table, by its row and its column, both counted from 0.
    """

    row: int = pydantic.Field()
    """
    The row, from 0.
    """

    column: int = pydantic.Field()
    """
    The column, from 0.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
