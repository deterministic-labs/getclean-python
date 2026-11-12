# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .money import Money


class KeyBudget(UniversalBaseModel):
    """
    The key's budget over one period.
    """

    amount: Money = pydantic.Field()
    """
    The budget for the period.
    """

    period: str = pydantic.Field()
    """
    The budget's period, as the account's billing names it, `month` for example.
    """

    spent: Money = pydantic.Field()
    """
    What the period has spent of the budget so far.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
