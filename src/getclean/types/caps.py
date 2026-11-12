# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .key_budget import KeyBudget
from .money import Money


class Caps(UniversalBaseModel):
    """
    The key's cap on one call and its budgets.
    """

    call_cap: Money = pydantic.Field()
    """
    The most one call may cost under this key; it is the default `max_cost`.
    """

    run_budget: typing.Optional[Money] = pydantic.Field(default=None)
    """
    What is left of the default run's budget. Present when the run has one.
    """

    key_budget: typing.Optional[KeyBudget] = pydantic.Field(default=None)
    """
    The key's budget over a period. Present when the account owner set one.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
