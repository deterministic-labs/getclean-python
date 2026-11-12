# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .cost import Cost
from .search_batch_counts import SearchBatchCounts
from .search_batch_result import SearchBatchResult


class SearchBatch(UniversalBaseModel):
    """
    The answer of `search_batch`: the tally first, then one result per item in input order, then the sum of the searches' costs.
    """

    counts: SearchBatchCounts = pydantic.Field()
    """
    How the items ended, by outcome kind, with the items skipped before any search; the six add up to the number of items.
    """

    results: typing.List[SearchBatchResult] = pydantic.Field()
    """
    One result per item, in input order.
    """

    cost: Cost = pydantic.Field()
    """
    The sum of the searches' costs, `units` summed by name; `ceiling` the whole call's.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
