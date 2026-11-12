# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class DroppedCounts(UniversalBaseModel):
    """
    The results that are not leads, by reason; every integer always present; the keys are the values `dropped_reason` takes.
    """

    not_relevant: int = pydantic.Field()
    """
    Results under the ranking model's cut-off.
    """

    undated: int = pydantic.Field()
    """
    Results with no detectable date, dropped under `undated` `hidden`.
    """

    max_per_domain: int = pydantic.Field()
    """
    Results past `ranking_max_per_domain` for their site.
    """

    blocked_domain: int = pydantic.Field()
    """
    Results on a site in `blocked_domains`.
    """

    outside_allowed: int = pydantic.Field()
    """
    Results on a site outside `allowed_domains`.
    """

    source_kind: int = pydantic.Field()
    """
    Results whose publisher's kind is outside `source_kinds`.
    """

    source_independence: int = pydantic.Field()
    """
    Results outside `source_independence`.
    """

    folded_copy: int = pydantic.Field()
    """
    Results grouped behind a lead as copies of it.
    """

    phrase_check: int = pydantic.Field()
    """
    Results that failed a quoted phrase.
    """

    exclusion_check: int = pydantic.Field()
    """
    Results that carried an excluded word.
    """

    beyond_max_candidates: int = pydantic.Field()
    """
    Results ranked past the cap on leads.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
