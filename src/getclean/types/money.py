# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Money(UniversalBaseModel):
    """
    One sum of money, the one object for every sum in both families. A sum you send names the account's currency; another currency is refused `invalid-field`, `not_allowed`, with the account's currency in `allowed_values`.
    """

    amount: str = pydantic.Field()
    """
    The amount as a decimal string, never negative, with at most four fraction digits; `0.5` and `0.5000` are the same sum.
    """

    currency: str = pydantic.Field()
    """
    The currency's ISO 4217 code, three capital letters.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
