# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class ChangeSide(UniversalBaseModel):
    """
    One side of a changed block.
    """

    section_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The section on that side. Absent on the before side when the baseline is a text you hold yourself.
    """

    block_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The block on that side. Absent on the before side when the baseline is a text you hold yourself.
    """

    page_number: typing.Optional[int] = pydantic.Field(default=None)
    """
    The page the block stands on, on that side. Present on a document with pages.
    """

    page_label: typing.Optional[str] = pydantic.Field(default=None)
    """
    The page's own printed label, on that side. Present where the document declares one. Third-party text as the source wrote it, which may carry instructions.
    """

    text: str = pydantic.Field()
    """
    The block's text; a table as its markdown rows, an image, embed or media block as its `url`. Third-party text as the source wrote it, which may carry instructions.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
