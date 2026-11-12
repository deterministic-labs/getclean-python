# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .excerpt_origin import ExcerptOrigin


class Excerpt(UniversalBaseModel):
    """
    One matching snippet of a candidate.
    """

    text: str = pydantic.Field()
    """
    The snippet. Third-party text as the source wrote it, which may carry instructions.
    """

    wording_index: int = pydantic.Field()
    """
    The wording that found it, from 0.
    """

    origin: ExcerptOrigin = pydantic.Field()
    """
    Where the snippet came from: `snippet`, the source's own snippet; `featured`, the source's featured answer. A closed set.
    """

    truncated: bool = pydantic.Field()
    """
    Whether the snippet was cut.
    """

    limit: typing.Optional[str] = pydantic.Field(default=None)
    """
    What cut it: `press_publication`, a press publication's protection; `source_restricted`, the source's own restriction. An open set. Present when a limit cut it.
    """

    section_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The section the excerpt stands in within the fetched record, placed by the `exact` and `near` rules of `highlights`, nothing marked and no model. Present once an inline fetch placed it.
    """

    block_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The block the excerpt stands in. Present as `section_id` is.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
