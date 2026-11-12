# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Rates(UniversalBaseModel):
    """
    The key's rate, the same figures the `RateLimit` headers carry on every answer.
    """

    requests_per_minute: int = pydantic.Field()
    """
    How many requests the key may make per minute.
    """

    concurrency: int = pydantic.Field()
    """
    How many calls the key may have in flight at once.
    """

    resets_at: dt.datetime = pydantic.Field()
    """
    When the current minute's window resets, RFC 3339 in UTC.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
