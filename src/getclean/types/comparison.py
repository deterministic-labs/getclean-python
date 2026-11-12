# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .block_change import BlockChange
from .comparison_counts import ComparisonCounts
from .comparison_side import ComparisonSide
from .notice import Notice


class Comparison(UniversalBaseModel):
    """
    The answer of `compare_contents`: both sides with their fingerprints, whether anything changed, the whole tally on every page, and the changes block by block, paged.
    """

    contents_id: str = pydantic.Field()
    """
    The current record.
    """

    expires_at: dt.datetime = pydantic.Field()
    """
    When the current record expires. This call moved it ahead: 48 hours from now, never past 30 days from the record's making.
    """

    baseline_contents_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The baseline record. Present when given.
    """

    current: ComparisonSide = pydantic.Field()
    """
    The current record's side.
    """

    baseline: ComparisonSide = pydantic.Field()
    """
    The baseline's side; `fetched_at` is absent when the baseline is a text you hold yourself.
    """

    changed: bool = pydantic.Field()
    """
    Whether anything differs; true with `changes` `[]` means the words are the same and only their inline formatting moved.
    """

    counts: ComparisonCounts = pydantic.Field()
    """
    The whole tally, on every page, before the rows.
    """

    changes: typing.List[BlockChange] = pydantic.Field()
    """
    The changes of this page, block by block; `[]` when none.
    """

    next_page_token: typing.Optional[str] = pydantic.Field(default=None)
    """
    The token for the next page of changes; pass it as `page_token`. Present while more remains, and a page that carries it always has at least one change.
    """

    notices: typing.List[Notice] = pydantic.Field()
    """
    This call's notices, `fingerprint_incomparable`, `paywall_declared`, `page_size_lowered`, `version_retiring`; `[]` when none.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
