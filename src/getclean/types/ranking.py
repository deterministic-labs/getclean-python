# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .ranking_merge import RankingMerge
from .ranking_order import RankingOrder
from .ranking_priority import RankingPriority
from .stratum import Stratum


class Ranking(UniversalBaseModel):
    """
    What ordered the list, each as applied.
    """

    reranked: bool = pydantic.Field()
    """
    Whether the ranking model ran.
    """

    reranker_version: typing.Optional[str] = pydantic.Field(default=None)
    """
    The ranking model's version. Present only when it ran; absent under `deterministic_only` and on `rerank_missing`.
    """

    min_score: typing.Optional[float] = pydantic.Field(default=None)
    """
    The ranking model's cut-off, 0 to 1. Present only when it ran.
    """

    instructions_applied: bool = pydantic.Field()
    """
    Whether `ranking_instructions` were applied.
    """

    priorities: typing.List[RankingPriority] = pydantic.Field()
    """
    The `ranking_priorities` applied; `[]` when none.
    """

    order: RankingOrder = pydantic.Field()
    """
    The `ranking_order` applied.
    """

    preferred_domains: typing.List[str] = pydantic.Field()
    """
    The `ranking_preferred_domains` applied; `[]` when none.
    """

    max_per_domain: typing.Optional[int] = pydantic.Field(default=None)
    """
    The `ranking_max_per_domain` applied. Present when set.
    """

    merge: RankingMerge = pydantic.Field()
    """
    How the sources' lists were merged into one; a closed set with one value.
    """

    strata: typing.List[Stratum] = pydantic.Field()
    """
    One entry per source and language that took part in the merge, with the leads each gave.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
