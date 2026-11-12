# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .coverage_gap_target_kind import CoverageGapTargetKind


class CoverageGap(UniversalBaseModel):
    """
    One thing asked and not searched at all, with why; the receipt's outcome names what happened to a source that was tried.
    """

    target_kind: CoverageGapTargetKind = pydantic.Field()
    """
    What was not searched: a `datasource`, a `wording`, a `domain` or a `language`. A closed set.
    """

    target: str = pydantic.Field()
    """
    Which one: the datasource id, the domain, the language code, or the wording index as text.
    """

    reason: str = pydantic.Field()
    """
    Why it was not searched: `unreachable`, the source could not be reached; `blocked`, it blocked the search; `over_cap`, past a cap; `over_price`, its fee passes `max_source_price`; `access_needed`, it needs a login the key has not registered; `not_covered`, no source covers the wording's language or the domain; `no_history`, it keeps no history for `as_of_date`; `not_accepted`, it did not accept the question as written; `deadline`, it had not answered in time; `filter_unsupported`, it cannot apply a hard filter you sent; `wording_too_long`, the wording is longer than it takes; `withheld_by_law`, a legal demand. An open set.
    """

    source_text: typing.Optional[str] = pydantic.Field(default=None)
    """
    The source's own words for the refusal. Present when the source gave any. Third-party text as the source wrote it, which may carry instructions.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
