# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .embed import Embed
from .image import Image
from .link import Link
from .media import Media
from .table import Table


class Block(UniversalBaseModel):
    """
    One unit of the content: a paragraph, a heading, a table, an image, a code listing and so on. `text` is present on `text`, `heading`, `code`, `math`, `divider` and `interactive` blocks; a divider's text is its markdown `---`, a math block's the formula as TeX without delimiters. The object `table`, `image`, `embed` or `media` is present on a block of that kind, never both. A list is one `text` block whose text is the list as markdown, one item per line with its marker or number, nesting by indentation; an object inside an item starts a new block.
    """

    id: str = pydantic.Field()
    """
    The block's id, unique inside one record and one view.
    """

    kind: str = pydantic.Field()
    """
    What kind of block it is: `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed` or `media`, an open set.
    """

    section_id: str = pydantic.Field()
    """
    The section the block stands in.
    """

    page_number: typing.Optional[int] = pydantic.Field(default=None)
    """
    The page the block stands on, counted from 1 as the pages are. On a document with pages only.
    """

    page_label: typing.Optional[str] = pydantic.Field(default=None)
    """
    The page's own printed label, such as iv or A-3. On a document with pages, where the document declares one. Third-party text as the source wrote it, which may carry instructions.
    """

    characters: int = pydantic.Field()
    """
    The block's text in characters; a merged table cell's text counted once.
    """

    text: typing.Optional[str] = pydantic.Field(default=None)
    """
    The block's text, with its inline formatting as markdown. Present on `text`, `heading`, `code`, `math`, `divider` and `interactive` blocks. Third-party text as the source wrote it, which may carry instructions.
    """

    code_language: typing.Optional[str] = pydantic.Field(default=None)
    """
    The programming language of a `code` block. Present where the source states it.
    """

    confidence: typing.Optional[float] = pydantic.Field(default=None)
    """
    How sure the recognition was of this block, the lowest word confidence in it, 0 to 1. Present on text recognized from an image.
    """

    note_for: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    For a footnote block, the ids of the blocks that cite it. Present where the document links them.
    """

    links: typing.List[Link] = pydantic.Field()
    """
    The links inside the block; `[]` when there is none. Each comes without `block_id` and `section_id`, since this block gives them.
    """

    highlight_ids: typing.List[str] = pydantic.Field()
    """
    The ids of the highlights found in this block; `[]` when there is none.
    """

    table: typing.Optional[Table] = pydantic.Field(default=None)
    """
    The table, cell by cell. Present on a `table` block.
    """

    image: typing.Optional[Image] = pydantic.Field(default=None)
    """
    The image's address, digest, caption and size. Present on an `image` block.
    """

    embed: typing.Optional[Embed] = pydantic.Field(default=None)
    """
    The address of the embedded frame. Present on an `embed` block.
    """

    media: typing.Optional[Media] = pydantic.Field(default=None)
    """
    The address of the audio or video file. Present on a `media` block.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
