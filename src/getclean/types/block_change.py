# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .block_change_kind import BlockChangeKind
from .cell_change import CellChange
from .change_side import ChangeSide


class BlockChange(UniversalBaseModel):
    """
    One change between the two sides, on one block.
    """

    kind: BlockChangeKind = pydantic.Field()
    """
    The kind of change: `added`, a block only on the current side; `removed`, only on the baseline side; `changed`, a paired block whose text differs; `moved`, the same text at another position. A closed set.
    """

    block_kind: str = pydantic.Field()
    """
    The block's kind, the after side's, or the before side's on a removal: `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed` or `media`; an open set.
    """

    before: typing.Optional[ChangeSide] = pydantic.Field(default=None)
    """
    The baseline side of the block. Absent on `added`.
    """

    after: typing.Optional[ChangeSide] = pydantic.Field(default=None)
    """
    The current side of the block. Absent on `removed`.
    """

    cells: typing.List[CellChange] = pydantic.Field()
    """
    The cell changes of a table block, rows paired before cells, an added row's cells with `before_text` absent and a removed row's with `after_text` absent; `[]` unless the block is a table.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
