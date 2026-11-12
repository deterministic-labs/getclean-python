# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class TableSpan(UniversalBaseModel):
    """
    One merged cell of a table: where it starts and how far it reaches.
    """

    row: int = pydantic.Field()
    """
    The row the cell starts in, from 0.
    """

    column: int = pydantic.Field()
    """
    The column the cell starts in, from 0.
    """

    row_span: int = pydantic.Field()
    """
    How many rows the cell covers, 1 or more.
    """

    column_span: int = pydantic.Field()
    """
    How many columns the cell covers, 1 or more.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
