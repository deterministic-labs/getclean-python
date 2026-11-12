# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .query_operator import QueryOperator
from .wording import Wording


class Interpretation(UniversalBaseModel):
    """
    How the question was read; every list present, `[]` when empty.
    """

    canonical_query: str = pydantic.Field()
    """
    The question as getclean read it; with no `query`, the identifiers' values joined by a space.
    """

    phrases: typing.List[str] = pydantic.Field()
    """
    The quoted phrases.
    """

    exclusions: typing.List[str] = pydantic.Field()
    """
    The excluded words.
    """

    operators: typing.List[QueryOperator] = pydantic.Field()
    """
    The operators read from the question.
    """

    wordings: typing.List[Wording] = pydantic.Field()
    """
    Every wording that ran, with its origin.
    """

    languages_searched: typing.List[str] = pydantic.Field()
    """
    The languages the wordings ran in, BCP 47 tags.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
