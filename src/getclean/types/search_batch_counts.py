# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class SearchBatchCounts(UniversalBaseModel):
    """
    How a batch's items ended; the six add up to the number of items, so you can read the tally before the results.
    """

    delivered: int = pydantic.Field()
    """
    Searches delivered: every source tried answered and everything asked ran.
    """

    partial: int = pydantic.Field()
    """
    Searches partial: something tried did not finish.
    """

    failed: int = pydantic.Field()
    """
    Searches failed: no source answered.
    """

    refused: int = pydantic.Field()
    """
    Searches refused: a rule stopped the search, and no source answered.
    """

    needs_person: int = pydantic.Field()
    """
    Searches that need a person before they can work.
    """

    skipped: int = pydantic.Field()
    """
    Items skipped before any search, each with its problem beside it in `results`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
