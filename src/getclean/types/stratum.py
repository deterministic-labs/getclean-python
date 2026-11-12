# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Stratum(UniversalBaseModel):
    """
    One source and language in the merge, with the leads it gave.
    """

    datasource_id: str = pydantic.Field()
    """
    The source, by its datasource id.
    """

    language: str = pydantic.Field()
    """
    The language, a BCP 47 tag.
    """

    lead_count: int = pydantic.Field()
    """
    The leads from this source in this language.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
