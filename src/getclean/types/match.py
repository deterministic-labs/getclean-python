# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Match(UniversalBaseModel):
    """
    One wording's hit on one source.
    """

    wording_index: int = pydantic.Field()
    """
    The wording that found it, by its index from 0.
    """

    datasource_id: str = pydantic.Field()
    """
    The datasource it was found on.
    """

    rank: int = pydantic.Field()
    """
    The position in that source's list for that wording, from 1.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
