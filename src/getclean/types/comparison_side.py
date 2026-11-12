# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class ComparisonSide(UniversalBaseModel):
    """
    One side of a comparison.
    """

    fetched_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    When the side's record was fetched. Absent when the side is a text you hold yourself.
    """

    fingerprint: str = pydantic.Field()
    """
    The side's fingerprint.
    """

    verified: bool = pydantic.Field()
    """
    True when getclean checked the side's fingerprint: always on a record, and on a text you hold yourself once its hash matched.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
