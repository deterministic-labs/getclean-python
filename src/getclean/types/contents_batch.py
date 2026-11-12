# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .contents_batch_counts import ContentsBatchCounts
from .contents_batch_result import ContentsBatchResult
from .cost import Cost


class ContentsBatch(UniversalBaseModel):
    """
    What `fetch_contents_batch` answers: the tally first, then one result per item in input order, then the sum of the records' costs.
    """

    counts: ContentsBatchCounts = pydantic.Field()
    """
    How the items ended, by outcome kind, with the items skipped before any fetch; the six add up to the number of items.
    """

    results: typing.List[ContentsBatchResult] = pydantic.Field()
    """
    One result per item, in the order of the request.
    """

    cost: Cost = pydantic.Field()
    """
    The sum of the records' costs, `units` summed by name; `ceiling` is the whole call's.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
