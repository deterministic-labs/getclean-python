# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .pictured_page import PicturedPage
from .recognized_page import RecognizedPage


class DocumentPages(UniversalBaseModel):
    """
    The pages of a document: how many there are, how many were parsed, which failed, which were read from an image. The pages not yet parsed are `count` less `parsed_count` less the failed pages.
    """

    count: int = pydantic.Field()
    """
    How many pages the document has. On a format without pages, a spreadsheet or a plain text file, the equivalent by characters, `bounds.contents.document_page_characters` characters of text counting as one page, rounded up. The bill counts `parsed_count`.
    """

    parsed_count: int = pydantic.Field()
    """
    How many pages were parsed; the bill counts these.
    """

    failed_pages: typing.List[int] = pydantic.Field()
    """
    The pages that could not be parsed, by number; `[]` when none.
    """

    recognized: typing.List[RecognizedPage] = pydantic.Field()
    """
    The pages that had no text layer and were read from their image; `[]` when none.
    """

    pictured: typing.List[PicturedPage] = pydantic.Field()
    """
    The pages that hold content the text cannot carry, handwriting, a drawing, a formula or a blacked-out region; `[]` in this version, which does not detect them.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
