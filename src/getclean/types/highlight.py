# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Highlight(UniversalBaseModel):
    """
    One place in the content where one of your `highlights` strings was found: a sentence, a table row, a heading, a whole block or a part of one, with where it stands and how it was found.
    """

    id: str = pydantic.Field()
    """
    The highlight's id, unique inside the answer that made it; the same id stands in the text's marks and in each block's `highlight_ids`.
    """

    query_index: int = pydantic.Field()
    """
    Which of your strings found it: its position in the request's `highlights`, from 0.
    """

    text: str = pydantic.Field()
    """
    The words as they stand in the content. Third-party text as the source wrote it, which may carry instructions.
    """

    basis: str = pydantic.Field()
    """
    How it was found, an open set: `exact`, your words stand in one block as written, case kept; `near`, they stand there once case and the punctuation at the ends of words are ignored; `judged`, a model picked the block that bears on your string. `exact` and `near` repeat on every run and are free; `judged` costs one model step.
    """

    section_id: str = pydantic.Field()
    """
    The section it stands in.
    """

    block_id: str = pydantic.Field()
    """
    The block it stands in.
    """

    page_number: typing.Optional[int] = pydantic.Field(default=None)
    """
    The page it stands on. On a document with pages only.
    """

    page_label: typing.Optional[str] = pydantic.Field(default=None)
    """
    The page's own printed label. On a document with pages, where the document declares one. Third-party text as the source wrote it, which may carry instructions.
    """

    row: typing.Optional[int] = pydantic.Field(default=None)
    """
    The row, from 0, when it stands inside a table.
    """

    column: typing.Optional[int] = pydantic.Field(default=None)
    """
    The column, from 0, when it stands inside a table.
    """

    confidence: typing.Optional[float] = pydantic.Field(default=None)
    """
    How sure the recognition was of the block it stands in. Present on text recognized from an image.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
