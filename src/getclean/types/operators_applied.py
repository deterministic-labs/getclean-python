# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .operator_applied import OperatorApplied


class OperatorsApplied(UniversalBaseModel):
    """
    One member per operator, every member always present, its state `not_applicable` for an operator the query did not use; `alternatives` stands for the `or` operator, since `or` is a reserved word.
    """

    phrase: OperatorApplied
    exclusion: OperatorApplied
    alternatives: OperatorApplied
    site: OperatorApplied
    filetype: OperatorApplied
    intitle: OperatorApplied
    inurl: OperatorApplied
    before: OperatorApplied
    after: OperatorApplied
    wildcard: OperatorApplied

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
