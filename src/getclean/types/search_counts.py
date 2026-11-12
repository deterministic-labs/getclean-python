# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .dropped_counts import DroppedCounts


class SearchCounts(UniversalBaseModel):
    """
    The counts describe the search, never a page; `found` equals `returned` plus every dropped count whatever ended the list.
    """

    returned: int = pydantic.Field()
    """
    The leads returned.
    """

    found: int = pydantic.Field()
    """
    The pages found before the cut.
    """

    dropped: DroppedCounts = pydantic.Field()
    """
    Why the rest are not leads, by reason.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
