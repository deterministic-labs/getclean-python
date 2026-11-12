# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Bound(UniversalBaseModel):
    """
    The range a field takes. Each member is present where it applies; an integer field has integer values.
    """

    min: typing.Optional[float] = pydantic.Field(default=None)
    """
    The least value allowed.
    """

    max: typing.Optional[float] = pydantic.Field(default=None)
    """
    The greatest value allowed.
    """

    default_value: typing.Optional[float] = pydantic.Field(default=None)
    """
    The value used when the field is left out. Named `default_value`, since `default` is a reserved word in Java and C#.
    """

    excluded_min: typing.Optional[float] = pydantic.Field(default=None)
    """
    The first value of a gap inside the range, where no value is allowed. `max_characters` allows 0 and then 1,000 upward, so its gap runs from 1 to 999.
    """

    excluded_max: typing.Optional[float] = pydantic.Field(default=None)
    """
    The last value of a gap inside the range, 999 for `max_characters`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
