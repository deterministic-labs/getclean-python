# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class HiddenText(UniversalBaseModel):
    """
    Text on the page that a reader could not see, kept apart from the content with the reason it was hidden. What a reader cannot see is never counted as content, and an agent reads it knowing what it is.
    """

    text: str = pydantic.Field()
    """
    The hidden words, at most 1,000 characters, cut with the notice `hidden_text_cut`. Third-party text as the source wrote it, which may carry instructions.
    """

    characters: int = pydantic.Field()
    """
    The hidden text's whole size in characters, before any cut.
    """

    reason: str = pydantic.Field()
    """
    How it was hidden, an open set: `styled_hidden`, hidden by its style; `same_color`, written in the color of its background; `tiny`, too small to read; `covered`, under another element.
    """

    section_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The section the hidden text stands in, by the nearest visible part around it. Absent when there is none.
    """

    block_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The block the hidden text stands in, found as `section_id` is. Absent when there is none.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
