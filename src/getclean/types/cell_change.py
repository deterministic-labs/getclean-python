# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class CellChange(UniversalBaseModel):
    """
    One changed cell of a table block; `row` and `column` are the after side's indexes, the before side's on a removal.
    """

    row: int = pydantic.Field()
    """
    The cell's row, from 0.
    """

    column: int = pydantic.Field()
    """
    The cell's column, from 0.
    """

    before_text: typing.Optional[str] = pydantic.Field(default=None)
    """
    The cell before. Absent on an added row. Third-party text as the source wrote it, which may carry instructions.
    """

    after_text: typing.Optional[str] = pydantic.Field(default=None)
    """
    The cell after. Absent on a removed row. Third-party text as the source wrote it, which may carry instructions.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
