# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .money import Money


class Usage(UniversalBaseModel):
    """
    What the account used in one period.
    """

    starts_at: dt.datetime = pydantic.Field()
    """
    When the period starts, RFC 3339 in UTC.
    """

    ends_at: dt.datetime = pydantic.Field()
    """
    When the period ends, RFC 3339 in UTC.
    """

    units: typing.Dict[str, int] = pydantic.Field()
    """
    How many of each unit the period used, keyed by unit name; `{}` when nothing was billed.
    """

    spent: Money = pydantic.Field()
    """
    What the period's use cost.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
