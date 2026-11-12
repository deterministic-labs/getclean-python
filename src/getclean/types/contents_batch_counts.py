# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class ContentsBatchCounts(UniversalBaseModel):
    """
    How a batch's items ended; the six add up to the number of items, so you can read the tally before the results.
    """

    delivered: int = pydantic.Field()
    """
    Records delivered: the content came whole or as the map, or the page was unchanged against its fingerprint.
    """

    partial: int = pydantic.Field()
    """
    Records partial: the work stopped in the middle and what was done is kept.
    """

    failed: int = pydantic.Field()
    """
    Records failed: nothing readable came from the source.
    """

    refused: int = pydantic.Field()
    """
    Records refused: a rule stopped the read, such as the address, the size, the type, a password, the robots file, the domain policy or a legal demand.
    """

    needs_person: int = pydantic.Field()
    """
    Records that need a person before they can work.
    """

    skipped: int = pydantic.Field()
    """
    Items skipped before any fetch, each with its problem beside it in `results`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
