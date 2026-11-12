# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .filter_applied import FilterApplied


class FiltersApplied(UniversalBaseModel):
    """
    One member per hard filter, every member always present.
    """

    allowed_domains: FilterApplied
    blocked_domains: FilterApplied
    published_from: FilterApplied
    published_until: FilterApplied
    published_within_days: FilterApplied
    undated: FilterApplied
    languages: FilterApplied
    media_types: FilterApplied
    safe_search: FilterApplied
    source_kinds: FilterApplied
    source_independence: FilterApplied
    as_of_date: FilterApplied

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
