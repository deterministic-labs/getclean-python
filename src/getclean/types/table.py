# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .cell_address import CellAddress
from .cell_confidence import CellConfidence
from .table_span import TableSpan


class Table(UniversalBaseModel):
    """
    A table as it is displayed, cell by cell, with its merged cells, its header rows and columns, and where its structure came from.
    """

    caption: typing.Optional[str] = pydantic.Field(default=None)
    """
    The table's caption; null when it has none. Third-party text as the source wrote it, which may carry instructions.
    """

    rows: typing.List[typing.List[str]] = pydantic.Field()
    """
    The rows, each a list of cells as displayed. A merged cell's text stands in every slot it covers, and an empty cell is the empty string, so every row has every column. Third-party text as the source wrote it, which may carry instructions.
    """

    spans: typing.List[TableSpan] = pydantic.Field()
    """
    The merged cells, each with its position and how many rows and columns it covers; `[]` when no cell merges.
    """

    header_rows: typing.List[int] = pydantic.Field()
    """
    Which rows are headers, by index from 0; `[]` when none.
    """

    header_columns: typing.List[int] = pydantic.Field()
    """
    Which columns are headers, by index from 0; `[]` when none.
    """

    basis: str = pydantic.Field()
    """
    Where the table's structure came from, an open set: `structure`, the source carries it; `layout`, read from the page's layout. In this version the tables of a PDF without structure and of a scan come as text, so `layout` does not occur.
    """

    last_page_number: typing.Optional[int] = pydantic.Field(default=None)
    """
    The last page the table continues onto. Present on a table that spans pages.
    """

    top_left_cell: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address of the top-left cell on the sheet, such as `B4`. On a spreadsheet only.
    """

    formula_cells: typing.Optional[typing.List[CellAddress]] = pydantic.Field(default=None)
    """
    The cells that held a formula, so you know which values were computed. On a spreadsheet only, `[]` when none.
    """

    cell_confidences: typing.Optional[typing.List[CellConfidence]] = pydantic.Field(default=None)
    """
    How sure the recognition was of each cell. Present on a table read from a page without a text layer.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
